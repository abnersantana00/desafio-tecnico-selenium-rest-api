# --- Dockerfile ---
FROM python:3.12-slim

# Instala dependências do sistema necessárias para psycopg2 e Chrome
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Define variáveis do Chrome (para Selenium funcionar no container)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

# Cria diretório de trabalho
WORKDIR /app

# Copia dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY app/ ./app
COPY initdb/ ./initdb

# Expõe a porta da API
EXPOSE 8000

# Comando para rodar a API com reload desativado (produção)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
