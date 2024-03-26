from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status, Form
from passlib.context import CryptContext
from pymongo import MongoClient
from pydantic import BaseModel, constr
from uuid import uuid4

# Criando uma instância da aplicação FastAPI
app = FastAPI(title="apidovincenzo  ")

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['pessoasdb']
collection = db['pessoas']

# Model para criar uma nova pessoa
class PessoaCreate(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
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
