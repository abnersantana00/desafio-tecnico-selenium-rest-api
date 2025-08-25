import re
from pathlib import Path
from datetime import datetime, timezone
import requests
# Funções Auxiliares (Scraper)

def baixar_pdfs(links, pasta: Path, URL: str = None):
    pasta.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0", "Referer": URL})
    total = len(links)
    for i, link in enumerate(links, start=1):
        arq = pasta / link.rsplit("/", 1)[-1]
        if arq.exists():
            continue
        with s.get(link, timeout=60, stream=True) as r:
            r.raise_for_status()
            with open(arq, "wb") as f:
                for bloco in r.iter_content(65536):
                    if bloco:
                       f.write(bloco)
        print(link)  
        print("Local Salvo:", pasta)



# Funções Auxiliares (0x0)






