FROM python:3.10-slim

WORKDIR /app

# Copie todos os arquivos do diretório atual para o diretório de trabalho no contêiner
COPY . .

# Instale as dependências do Python
RUN pip install -r requirements.txt

# Exponha a porta 8000 para acesso externo
EXPOSE 8000

# Comando padrão para iniciar o aplicativo Python

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --proxy-headers
