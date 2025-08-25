ChatGPT said:

Perfeito 🙌
Aqui está o conteúdo já formatado em Markdown, pronto para você copiar e colar no seu README.md do GitHub:

# 📘 Desafio Técnico – Selenium + FastAPI + Docker

Este projeto implementa um **scraper automatizado com Selenium** integrado a uma **API em FastAPI**, que:

- Captura os **Diários Oficiais do Município (DOM)** no site da prefeitura.  
- Faz **upload para o serviço 0x0.st** (file hosting).  
- Persiste os metadados (data de publicação + link) em um banco **PostgreSQL**.  
- Permite acessar os PDFs localmente, consultar por competência e gerenciar os registros.  

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12+**
- **FastAPI**
- **Selenium (Chromium headless)**
- **SQLAlchemy + PostgreSQL**
- **Docker + Docker Compose**

---

## 📂 Estrutura do Projeto



├── app/
│ ├── main.py # API FastAPI (endpoints principais)
│ ├── crud.py # Operações no banco de dados
│ ├── prefeitura_scraper.py # Lógica do Selenium (captura dos DOMs)
│ ├── prefeitura_upload.py # Upload dos arquivos para 0x0.st
│ ├── utils.py # Funções auxiliares
│
├── data/ # Armazena PDFs baixados (montado via Docker)
│
├── initdb/
│ └── 01_schema.sql # Script de inicialização do banco
│
├── docker-compose.yml # Orquestra API + DB + PgAdmin
├── dockerfile # Build da API
├── requirements.txt # Dependências Python
└── README.md # Este manual




## 🚀 Como Rodar no Docker Compose

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
docker-compose up --build


Isso irá levantar:

API FastAPI em http://localhost:8000

Banco PostgreSQL em localhost:5432

PgAdmin4 em http://localhost:5050



📖 Documentação dos Endpoints
🔹 GET /

Lista todas as publicações armazenadas no banco.

Exemplo de resposta:
{
  "ok": true,
  "total": 5,
  "itens": [
    {"id": 1, "data": "2019-05-02", "link": "https://0x0.st/K-qO.pdf"},
    {"id": 2, "data": "2019-05-03", "link": "https://0x0.st/K-q3.pdf"}
  ]
}


GET ou POST /add/{ano}/{mes}

Executa o scraper Selenium, faz upload dos PDFs para 0x0.st e persiste no banco.

⚠️ Esse endpoint pode demorar alguns segundos porque executa (Selenium + 0x0 + SQL )

GET http://localhost:8000/add/2019/05

{
  "ok": true,
  "mensagem": "Scraper finalizado para 2019-05",
  "salvos": 10
}

🔹 GET /listar/{ano}/{mes}

Lista todas as publicações de um mês específico.

Exemplo:

GET http://localhost:8000/listar/2019/05


{
  "ok": true,
  "ano": 2019,
  "mes": "05",
  "total": 10,
  "itens": [
    {"id": 1, "data": "2019-05-02", "link": "https://0x0.st/K-qO.pdf"},
    {"id": 2, "data": "2019-05-03", "link": "https://0x0.st/K-q3.pdf"}
  ]
}


ET /data/{ano}/{mes}

Lista os arquivos locais já baixados no servidor.

Exemplo:

GET http://localhost:8000/data/2019/05

{
  "ok": true,
  "pasta": "/app/data/2019-05",
  "total": 2,
  "arquivos": [
    {"nome": "dom_20190502_xxx.pdf", "url": "http://localhost:8000/files/2019-05/dom_20190502_xxx.pdf"},
    {"nome": "dom_20190503_yyy.pdf", "url": "http://localhost:8000/files/2019-05/dom_20190503_yyy.pdf"}
  ]
}