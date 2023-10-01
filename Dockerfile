# Use a imagem base do Python
FROM python:3.11

# Copie o código-fonte do seu aplicativo para o contêiner
COPY . /app

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Instale as dependências do aplicativo
RUN pip install -r requirements.txt

# Exponha a porta em que seu aplicativo está sendo executado (se necessário)
EXPOSE 8000

# Comando para iniciar seu aplicativo quando o contêiner for iniciado
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
