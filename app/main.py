from fastapi import FastAPI, Request, HTTPException

from datetime import date
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles
from app import prefeitura_scraper, prefeitura_upload, crud
import shutil

# --- App ---
app = FastAPI(title="Desafio Técnico - Selenium + API")

# inicializa schema do BD
crud.init_db()

# arquivos estáticos
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(DATA_DIR)), name="files")

# --- Rotas ---

# Listar todos os itens (DATA, LINK 0x0)
@app.get("/")
def list_all():
    itens = crud.listar_todas()
    return {"ok": True, "total": len(itens), "itens": itens}

# Adicionar (Capturar PDFs + Enviar para 0x0 + Persistir no Banco de Dados)
# demora alguns segundos porque faz as 3 tarefas (Selenium + 0x0 + SQL)
@app.api_route("/add/{ano}/{mes}", methods=["GET", "POST"])
def add_pub(ano: str, mes: str):
    prefeitura_scraper.baixar_dom(ano, mes)
    links = prefeitura_upload.prefeitura_upload(ano=ano, mes=mes)
    total = crud.salvar_bd(links)
    return {"ok": True, "mensagem": f"Scraper finalizado para {ano}-{mes}", "salvos": total}

# listar por competência (AAAA/MM) 
@app.get("/listar/{ano}/{mes}")
def listar_por_ano_mes(ano: int, mes: int):
    itens = crud.listar_por_ano_mes(ano, mes)
    return {"ok": True, "ano": ano, "mes": f"{mes:02d}", "total": len(itens), "itens": itens}

# Acessar os PDFs locamente na pasta http://localhost:8000/data/AAAA/MM
@app.get("/data/{ano}/{mes}")
def listar_dados(ano: str, mes: str, request: Request):
    mes = mes.zfill(2)
    pasta = DATA_DIR / f"{ano}-{mes}"
    if not pasta.is_dir():
        raise HTTPException(status_code=404, detail=f"Pasta {pasta} não encontrada")
    
    arquivos = sorted([p for p in pasta.iterdir() if p.is_file()])
    if not arquivos:
        return {"ok": True, "pasta": str(pasta), "total": 0, "arquivos": []}

    base = str(request.base_url).rstrip("/")  
    itens = [
        {
            "nome": arq.name,
            "url": f"{base}/files/{ano}-{mes}/{arq.name}"
        }
        for arq in arquivos
    ]
    return {"ok": True, "pasta": str(pasta), "total": len(itens), "arquivos": itens}

# Deleta tudo que está na pasta localhost
@app.get("/delete")
def delete_all():
    if not DATA_DIR.exists():
        return {"ok": False, "msg": "Pasta base não encontrada"}
    pastas = [p for p in DATA_DIR.iterdir() if p.is_dir() and "-" in p.name]
    for pasta in pastas:
        shutil.rmtree(pasta, ignore_errors=True)
    return {"ok": True, "deletadas": [p.name for p in pastas]}


# Deleta todos os registros dos links no BD
@app.get("/delete_bd")
def delete_bd():
    return crud.delete_all_rows()