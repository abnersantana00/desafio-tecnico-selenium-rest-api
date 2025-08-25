# 📘 Desafio Técnico – Selenium + FastAPI + Docker

Este projeto implementa um **scraper automatizado com Selenium** integrado a uma **API**, que:

- Captura os **Diários Oficiais do Município (DOM)** no site da prefeitura: https://www.natal.rn.gov.br/dom  
- Faz **upload para o serviço 0x0.st** (file hosting).  
- Persiste os dados (data de publicação + link) em um banco **PostgreSQL**.  
- Permite acessar os PDFs localmente, consultar por competência e gerenciar os registros.  

---


## 🚀 Rodar o Docker Compose Localmente

```bash
git clone https://github.com/abnersantana00/desafio-tecnico-selenium-rest-api.git
```

```bash
cd desafio-tecnico-selenium-rest-api
```
```bash
docker-compose up --build
```



## 🚀 Isso irá levantar:

API FastAPI em http://localhost:8000

Banco PostgreSQL em http://localhost:5432

PgAdmin4 em http://localhost:5050

---


## 🧪 Teste rápido (Roteiro)
1. GET /add/2025/07 — baixa PDF, envia para 0x0.st e salva os links gerados no PostgreSQL
2. GET /listar/2025/07 — valida o que entrou no BD.
3. GET /data/2025/07 — confirma se existe PDFs local e URLs públicas.
4. (Opcional) GET /delete e GET /delete_bd — limpeza. (Remove dados Locais e Remove Dados no Banco de Dados)
---

#### Listar todas as publicações armazenadas no banco 

```bash
  http://localhost:8000/
```
#### Resposta Esperada 
```bash
{
  "ok": true,
  "total": 5,
  "itens": [
    {"id": 1, "data": "2019-05-02", "link": "https://0x0.st/K-qO.pdf"},
    {"id": 2, "data": "2019-05-03", "link": "https://0x0.st/K-q3.pdf"}
  ]
}
```

---
#### Executar Scraping + Upload 0x0 + salvar no BD (pode demorar alguns segundos pra executar)

```bash
  http://localhost:8000/add/AAAA/MM
```
#### Resposta Esperada 
```bash
{
  "ok": true,
  "mensagem": "Scraper finalizado para 2025-07",
  "salvos": 10
}
```

---

#### Listar publicações (links) 0x0 por competência (MÊS e ANO)
```bash
  http://localhost:8000/listar/AAAA/MM
```
#### Resposta Esperada 
```bash
 {
  "ok": true,
  "ano": 2025,
  "mes": "07",
  "total": 10,
  "itens": [
    {"id": 1, "data": "2019-05-02", "link": "https://0x0.st/K-qO.pdf"},
    {"id": 2, "data": "2019-05-03", "link": "https://0x0.st/K-q3.pdf"}
  ]
}

```

---

#### Listar PDFs locais por competência

```bash
 http://localhost:8000/data/2025/07
```
#### Resposta Esperada 

```bash
{
  "ok": true,
  "pasta": "/app/data/2019-05",
  "total": 2,
  "arquivos": [
    {
      "nome": "dom_20190502_eba502294c9b98092c51a0098168c45f.pdf",
      "url": "http://localhost:8000/files/2019-05/dom_20190502_eba502294c9b98092c51a0098168c45f.pdf"
    },
    {
      "nome": "dom_20190503_7b46eddd18700c4d8be9f206371ac912.pdf",
      "url": "http://localhost:8000/files/2019-05/dom_20190503_7b46eddd18700c4d8be9f206371ac912.pdf"
    }
  ]
}
```



---

#### Deletar todos os PDFs locais

```bash
 http://localhost:8000/delete
```
#### Resposta Esperada 

```bash
{
  "ok": true,
  "deletadas": ["2019-05", "2020-03"]
}
```
Observações
- Irreversível: apaga arquivos locais baixados
- Não afeta os registros no banco de dados (use /delete_bd para o BD)

---

#### Deletar todos os registros do Banco de Dados PostgreSQL

```bash
 http://localhost:8000/delete_bd
```
#### Resposta Esperada 

```bash
{
  "ok": true,
  "mensagem": "Todos os registros foram apagados"
}
```
Observações
- Irreversível: apaga arquivos locais baixados
- Não afeta os registros no banco de dados (use /delete_bd para o BD)





### ⚠️  Atenção — Problemas ao Enviar PDFs do DOM da Prefeitura ⚠️

Durante o envio de alguns PDFs do Diário Oficial do Município (DOM), foram identificados erros específicos de acesso aos arquivos.

### Erro Reportado

- HTTP 451 – Unavailable For Legal Reasons (Indisponível por razões legais)

Esse erro ocorre quando determinados documentos não podem ser acessados devido a restrições legais ou bloqueios aplicados pelo próprio site da Prefeitura.

### Observações Importantes

O problema não afeta todos os documentos.

Em períodos específicos (ex.: 07/2025), todos os PDFs deixam de estar disponíveis para envio no site 0x0.st.

Após a indisponibilidade inicial, mesmo tentando reenviar o documento, o sistema não aceita mais o arquivo.

```bash
Tentativa de envio em 07/2025:
-> HTTP 451 Unavailable For Legal Reasons
-> Documento não pôde ser acessado novamente
```


O codigo-fonte tambem esta disponivel no Google Drive :
- https://drive.google.com/drive/folders/1f0KUQTP1TLaiKo1JAao81Y8AGQ8nGqgO?usp=sharing
  
Captura de Tela do (Link Local e do Link 0x0.st  
- https://drive.google.com/open?id=1lwAFkVrvw6m5NZTBwcOwoaSCem92QfTX&usp=drive_fs
