#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coleta todos os PDFs do Diário Oficial do Município de Natal (DOM) do **mês anterior**.

- Acessa https://www.natal.rn.gov.br/dom (via Selenium, somente para validar disponibilidade)
- Usa a **API oficial** que a própria página chama (DataTables):
  https://www.natal.rn.gov.br/api/dom/data/<MM>/<AAAA>
- Extrai todos os links dos PDFs e baixa para data/YYYY-MM (evita paginação da tabela)

Requisitos: Python 3.9+, Chrome/Chromium, selenium>=4.6 (Selenium Manager), requests, beautifulsoup4
Instalação: pip install selenium requests beautifulsoup4

"""
from __future__ import annotations
import sys
import re
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.natal.rn.gov.br/dom"
API_URL = "https://www.natal.rn.gov.br/api/dom/data/{mm}/{yyyy}"

# ---------- utilidades ----------
def mes_anterior(hj: date | None = None):
    hj = hj or date.today()
    ano, mes = hj.year, hj.month - 1
    if mes == 0:
        mes, ano = 12, ano - 1
    return ano, mes


def nova_sessao_http() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=0.6, status_forcelist=(500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    })
    return s


def novo_driver(headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1366,900")
    return webdriver.Chrome(options=opts)  # Selenium Manager resolve o driver


# ---------- coleta de links ----------

def _hrefs_no_html_anchor(html_anchor: str) -> list[str]:
    """Extrai hrefs de uma string com tags <a> vinda da API DataTables."""
    soup = BeautifulSoup(html_anchor, "html.parser")
    return [a.get("href") for a in soup.find_all("a", href=True)]


def listar_pdfs_via_api(sess: requests.Session, mm: int, yyyy: int) -> list[str]:
    url = API_URL.format(mm=f"{mm:02d}", yyyy=yyyy)
    r = sess.get(url, timeout=60)
    r.raise_for_status()
    payload = r.json()

    data = payload.get("data") or payload  # alguns ambientes retornam só a lista
    pdfs: list[str] = []
    for row in data:
        # normalmente row é um dict {"0": "<a href=...>...</a>"}
        if isinstance(row, dict):
            val = row.get("0") or ""
            hrefs = _hrefs_no_html_anchor(val)
        else:
            # fallback: string crua
            hrefs = _hrefs_no_html_anchor(str(row))
        for h in hrefs:
            if ".pdf" in (h or "").lower():
                pdfs.append(h)
    # remove duplicados preservando ordem
    seen = set()
    uniq = []
    for u in pdfs:
        if u and u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq


def descobrir_pdf(drv, url: str, timeout: int = 15) -> str | None:
    """Para casos raros onde o link não é direto para .pdf, tenta descobrir dentro da página."""
    if url.lower().endswith(".pdf") or ".pdf" in url.lower():
        return url
    origem = drv.current_window_handle
    drv.execute_script("window.open(arguments[0], '_blank');", url)
    drv.switch_to.window(drv.window_handles[-1])
    try:
        WebDriverWait(drv, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        anchors = drv.find_elements(By.XPATH, "//a[contains(translate(@href, 'PDF', 'pdf'), '.pdf')]")
        if anchors:
            return anchors[0].get_attribute("href")
        for sel in ("//embed[contains(translate(@src, 'PDF','pdf'), '.pdf')]",
                    "//iframe[contains(translate(@src, 'PDF','pdf'), '.pdf')]"):
            els = drv.find_elements(By.XPATH, sel)
            if els:
                return els[0].get_attribute("src")
        return None
    finally:
        try:
            drv.close()
            drv.switch_to.window(origem)
        except Exception:
            pass


# ---------- download ----------

def baixar(sess: requests.Session, url: str, pasta: Path) -> Path | None:
    nome = Path(urlparse(url).path).name or "arquivo.pdf"
    if not nome.lower().endswith(".pdf"):
        nome += ".pdf"
    destino = pasta / nome
    if destino.exists():
        return None
    with sess.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, "wb") as f:
            for chunk in r.iter_content(1 << 15):
                if chunk:
                    f.write(chunk)
    return destino


# ---------- fluxo principal ----------

def main():
    yyyy, mm = mes_anterior()
    outdir = Path("data") / f"{yyyy}-{mm:02d}"

    sess = nova_sessao_http()

    # 1) (Opcional) abrir a página só para garantir disponibilidade
    drv = None
    try:
        drv = novo_driver(headless=True)
        drv.get(BASE_URL)
        WebDriverWait(drv, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        # Se falhar, seguimos mesmo assim pois a API é pública
        pass

    # 2) Coleta via API (mais estável e inclui todas as páginas)
    pdf_links = listar_pdfs_via_api(sess, mm, yyyy)

    # 3) Fallback: se algum link não terminar com .pdf, tenta descobrir via Selenium
    if drv and pdf_links:
        resolvidos = []
        for u in pdf_links:
            p = descobrir_pdf(drv, u) or u
            resolvidos.append(p)
        pdf_links = resolvidos

    if not pdf_links:
        print("Nenhum PDF encontrado para o período.")
        return 2

    baixados = 0
    for url in pdf_links:
        salvo = baixar(sess, url, outdir)
        if salvo:
            baixados += 1
            print(salvo)
    print(f"Concluído. PDFs novos baixados: {baixados}. Total encontrado: {len(pdf_links)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
