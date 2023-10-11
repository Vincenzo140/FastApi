from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
from pymongo import MongoClient
import uuid

app = FastAPI()


client = MongoClient('mongodb://localhost:27017/')
db = client['pessoasdb']  
collection = db['pessoas']  

class PessoaCreate(BaseModel):
    apelido: constr(max_length=32)
    nome: constr(max_length=100)
    nascimento: int  
    stack: list[str] = None

class PessoaResponse(BaseModel):
    id: str
    apelido: str
    nome: str
    nascimento: int  
    stack: list[str] = None

@app.post('/pessoas', response_model=PessoaResponse, status_code=201)
def create_pessoa(pessoa: PessoaCreate):
    
    existing_pessoa = collection.find_one({'apelido': pessoa.apelido})
    if existing_pessoa:
        raise HTTPException(status_code=422, detail="Apelido já existe")


    new_pessoa = {
        'id': str(uuid.uuid4()),
        'apelido': pessoa.apelido,
        'nome': pessoa.nome,
        'nascimento': pessoa.nascimento,
        'stack': pessoa.stack
    }
    collection.insert_one(new_pessoa)

    return new_pessoa

@app.get('/pessoas/{id}', response_model=PessoaResponse)
async def find_by_id(id: str):
    
    pessoa = collection.find_one({'id': id})
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return pessoa

@app.get('/pessoas', response_model=list[PessoaResponse])
def find_by_term(term: str = Query(..., min_length=1)):

    results = []
    cursor = collection.find()
    for pessoa in cursor:
        if term.lower() in pessoa['apelido'].lower() or term.lower() in pessoa['nome'].lower() or (pessoa['stack'] and any(term.lower() in stack_item.lower() for stack_item in pessoa['stack'])):
            results.append(pessoa)
    return results

@app.get("/contagem-pessoas")
def count_pessoas():
    
    count = collection.count_documents({})
    return count
