from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr
from pymongo import MongoClient
import uuid

client = MongoClient("mongodb://user_root:pass_root@db:27017")
db = client["Projetinho"]["pessoas"]

app = FastAPI()

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

@app.post('/pessoas', response_model=PessoaResponse, status_code=201)
def create_pessoa(pessoa: PessoaCreate):

    new_pessoa = {
        'id': str(uuid.uuid4()),
        'apelido': pessoa.apelido,
        'nome': pessoa.nome,
        'nascimento': pessoa.nascimento,
        'stack': pessoa.stack
    }
    
    db.insert_one(new_pessoa)

    return new_pessoa

@app.get('/pessoas/{id}', response_model=PessoaResponse)
async def find_by_id(id: str):
    pessoa = db.find_one({"id": id})
    if pessoa:
        return pessoa
    raise HTTPException(status_code=404, detail="Pessoa não encontrada")

@app.get('/pessoas', response_model=list[PessoaResponse])
def find_by_term(term: str = Query(..., min_length=1)):
    results = list(db.find({
        "$or": [
            {"apelido": {"$regex": term, "$options": "i"}},
            {"nome": {"$regex": term, "$options": "i"}},
            {"stack": {"$elemMatch": {"$regex": term, "$options": "i"}}}
        ]
    }))
    return results

@app.get("/contagem-pessoas")
def count_pessoas():
    count = db.count_documents({})
    return count

@app.get("/teste_db")
def teste_db():
    ping = client.server_info()
    return {"ping": ping}
