# prefeitura_scraper.py
import time
import tempfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .utils import baixar_pdfs

URL = "https://www.natal.rn.gov.br/dom"
ANO, MES = "2022", "07"
SAIDA = Path(f"data/{ANO}-{MES}")

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")        # headless moderno
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")

    # cria perfil temporário p/ evitar conflito
    tmp_profile = tempfile.mkdtemp()
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    service = Service("/usr/bin/chromedriver")  # dentro do container chromium-driver
    return webdriver.Chrome(service=service, options=opts)

def baixar_dom(ano: str, mes: str):
    
    driver = make_driver()
    try:
        driver.get(URL)
        time.sleep(0.5)
        
        Select(driver.find_element(By.NAME, "mes")).select_by_value(mes)
        Select(driver.find_element(By.NAME, "ano")).select_by_value(ano)
        driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.m-2").click()
        time.sleep(0.5)

        Select(driver.find_element(By.NAME, "example_length")).select_by_value("100")
        time.sleep(0.5)

        links = [a.get_attribute("href")
                 for a in driver.find_elements(By.CSS_SELECTOR, "table#example tbody a")]
        print(f"Iniciando download de {len(links)} arquivos...")
        saida = Path(f"data/{int(ano):04d}-{int(mes):02d}")
        baixar_pdfs(links, pasta=saida,  URL=URL)
        print(f"✅ Downloads concluídos. {saida.resolve()}")
   
    finally:
        driver.quit()
    