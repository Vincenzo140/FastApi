import logging
import os
from datetime import datetime
from typing import List, Optional

import logging
import os
import time, datetime 
from typing import Optional
from .lib_fastapi import FastApiObservability
from .lib_log import Logger
from .lib_metrics import Metrics
import uvicorn
import psutil
import httpx
from fastapi import FastAPI, Response
from opentelemetry.propagate import inject
from utils import PrometheusMiddleware, setting_otlp

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pydantic import BaseModel, constr
from uuid import uuid4

# Importando os pacotes do MongoDB
from pymongo import MongoClient


METRICS_EXPORTER_URL = os.environ.get("METRICS_EXPORTER_URL")
TRACES_EXPORTER_URL = os.environ.get("TRACES_EXPORTER_URL")
LOGS_EXPORTER_URL = os.environ.get("LOGS_EXPORTER_URL")
APP_NAME = os.environ.get("APP_NAME")
APP_HOST = os.environ.get("APP_HOST")
APP_PORT = os.environ.get("APP_PORT")
APP_VERSION = os.environ.get("APP_VERSION")
LOG_FILE = os.environ.get("LOG_FILE")

fastApiObservability = FastApiObservability(path="", name=APP_NAME, version=APP_VERSION)

# Criando uma instância da aplicação FastAPI
app = FastAPI(title="apidovincenzo")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)




# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['pessoasdb']
collection = db['pessoas']


class PessoaCreate(BaseModel):
    apelido: str
    nome: str
    nascimento: str
    stack: Optional[List[str]] = None

# Model para resposta
class PessoaResponse(BaseModel):
    id: str
    apelido: str
    nome: str
    nascimento: int
    stack: Optional[List[str]] = None

# Endpoint para criar uma nova pessoa
@app.post('/pessoas', response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def create_pessoa(pessoa: PessoaCreate):
    # Converta a data para o formato desejado
    nascimento = datetime.strptime(pessoa.nascimento, "%Y-%m-%d").timestamp()

    existing_pessoa = collection.find_one({'apelido': pessoa.apelido})
    if existing_pessoa:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Apelido já existe")

    new_pessoa = {
        'id': str(uuid4()),
        'apelido': pessoa.apelido,
        'nome': pessoa.nome,
        'nascimento': nascimento,
        'stack': pessoa.stack
    }
    collection.insert_one(new_pessoa)
    return new_pessoa

# Endpoint para atualizar informações de uma pessoa por ID
@app.put('/pessoas/{id}', response_model=PessoaResponse)
async def update_pessoa(id: str, pessoa_update: PessoaCreate):
    existing_pessoa = collection.find_one({'id': id})
    if not existing_pessoa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pessoa não encontrada")

    # Converta a data para o formato desejado
    nascimento = datetime.strptime(pessoa_update.nascimento, "%Y-%m-%d").timestamp()

    # Atualize as informações da pessoa
    updated_pessoa = {
        '$set': {
            'apelido': pessoa_update.apelido,
            'nome': pessoa_update.nome,
            'nascimento': nascimento,
            'stack': pessoa_update.stack
        }
    }
    collection.update_one({'id': id}, updated_pessoa)

    # Recupere a pessoa atualizada
    updated_pessoa = collection.find_one({'id': id})
    return updated_pessoa

# Endpoint para excluir uma pessoa por ID
@app.delete('/pessoas/{id}', response_model=PessoaResponse)
async def delete_pessoa(id: str):
    existing_pessoa = collection.find_one({'id': id})
    if not existing_pessoa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pessoa não encontrada")

    # Remova a pessoa
    collection.delete_one({'id': id})

    return existing_pessoa

# Endpoint para recuperar todas as pessoas
@app.get('/pessoas', response_model=List[PessoaResponse])
def get_pessoas():
    pessoas = collection.find()
    return list(pessoas)

# ... Código restante ...

if __name__ == "__main__":

    logConfig = Logger(appName=APP_NAME, name=APP_NAME, level=logging.DEBUG)
    # logConfig.setLogFile(path=LOG_FILE)
    logConfig.setLogExporter(url=LOGS_EXPORTER_URL)
    logConfig.setLogConsole()
    logConfig.setFormatter()
    logConfig.setBasicConfig()
    fastApiObservability.setInstrumentorTraces(grpc=True, url=TRACES_EXPORTER_URL)
    
    uvicorn.run(
        app,
        host=APP_HOST,
        port=int(APP_PORT),
        log_config=logConfig.getConfig()
    )
