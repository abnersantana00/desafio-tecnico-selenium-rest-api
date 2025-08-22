# Desafio Técnico #

Este repositório contém a implementação do desafio técnico proposto.  
O objetivo é demonstrar conhecimentos em **[linguagem/tecnologias utilizadas]**, boas práticas de código e organização do projeto.  

---

## 🚀 Tecnologias Utilizadas
- [x] Python    
- [x] Banco de Dados: PostgreSQL  
- [x] Docker  

---

## 🚀 Como usar:

- [x] Crie um venv e instale : 
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install --upgrade pip
pip install selenium webdriver-manager requests
- [x] Execute
python scraper_dom_natal.py

## 📂 Estrutura do Projeto

# subir os serviços
docker compose up -d

# ver os logs até o schema ser criado
docker compose logs -f postgres

# acessar via psql
docker exec -it dom-postgres psql -U domuser -d domdb