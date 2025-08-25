from pathlib import Path
import sys
import requests
import re
from datetime import datetime, timezone

URL = "https://0x0.st"


def salvar_metadados(pdf: Path, link: str) -> dict:
    return {"data_publicacao": extrair_data(pdf), "link": link.strip()}


def extrair_data(pdf: Path) -> str:
    m = re.search(r"dom_(\d{4})(\d{2})(\d{2})", pdf.name)
    if m:
        ano, mes, dia = m.groups()
        return f"{ano}-{mes}-{dia}"
    dt = datetime.fromtimestamp(pdf.stat().st_mtime, tz=timezone.utc).date()
    return dt.isoformat()


def prefeitura_upload(ano: str, mes: str) -> list[dict]:
    raiz = Path(f"data/{ano}-{mes}")
    print("Raiz:", raiz)
    if not raiz.is_dir():
        print(f"[ERRO] Pasta não encontrada: {raiz.resolve()}", file=sys.stderr)
        return []

    s = requests.Session()
    s.headers.update({"User-Agent": "user-uploader/1.0"})

    resultados = []
    for pdf in sorted(raiz.rglob("*.pdf")):
        try:
            with pdf.open("rb") as f:
                r = s.post(URL, files={"file": (pdf.name, f, "application/pdf")}, timeout=60)
                r.raise_for_status()
                meta = salvar_metadados(pdf, r.text)
                print(f"[sucesso!] : {pdf} -> {meta['link']} ({meta['data_publicacao']})")
                resultados.append(meta)
        except Exception as e:
            print(f"[falha!] {pdf} -> {e}", file=sys.stderr)

    return resultados