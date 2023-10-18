from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, constr
from pymongo import MongoClient

import uuid

app = FastAPI()


from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://vincenzo:12345@vincenzo04.zbawqax.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

class PessoaCreate(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: str
    stack: list[str] = None

class PessoaResponse(BaseModel):
    id: str
    apelido: str
    nome: str
    nascimento: str
    stack: list[str] = None

pessoas = []

@app.post('/pessoas', response_model=PessoaResponse, status_code=201)
def create_pessoa(pessoa: PessoaCreate):

    for existing_pessoa in pessoas:
        if existing_pessoa['apelido'] == pessoa.apelido:
            raise HTTPException(status_code=422, detail="Apelido já existe")

    try:
        nascimento = pessoa.nascimento.split('-')
        if len(nascimento) != 3:
            raise ValueError()
        year, month, day = map(int, nascimento)
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=422, detail="Data de nascimento inválida")

    if pessoa.stack:
        for item in pessoa.stack:
            if not isinstance(item, str) or len(item) > 32:
                raise HTTPException(status_code=422, detail="Stack inválido")

    new_pessoa = {
        'id': str(uuid.uuid4()),
        'apelido': pessoa.apelido,
        'nome': pessoa.nome,
        'nascimento': pessoa.nascimento,
        'stack': pessoa.stack
    }

    pessoas.append(new_pessoa)

    return new_pessoa

@app.get('/pessoas/{id}', response_model=PessoaResponse)
async def find_by_id(id: str):
    for pessoa in pessoas:
        if pessoa['id'] == id:
            return pessoa
    raise HTTPException(status_code=404, detail="Pessoa não encontrada")

@app.get('/pessoas', response_model=list[PessoaResponse])
def find_by_term(term: str = Query(..., min_length=1)):
    results = []
    for pessoa in pessoas:
        if term.lower() in pessoa['apelido'].lower() or term.lower() in pessoa['nome'].lower() or (pessoa['stack'] and any(term.lower() in stack_item.lower() for stack_item in pessoa['stack'])):
            results.append(pessoa)
    return results

@app.get("/contagem-pessoas")
def count_pessoas():
    return len(pessoas)
