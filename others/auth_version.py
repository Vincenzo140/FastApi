from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from pydantic import BaseModel, constr
from uuid import uuid4

class SomeDatabase:
    def get_user(self, username: str):
        # Este é um exemplo fictício, você precisará ajustar isso para a sua aplicação
        hashed_password = pwd_context.hash("senha_secreta")  # Simulando uma senha hash
        return UserInDB(username=username, hashed_password=hashed_password)


class UserInDB:
    def __init__(self, username: str, hashed_password: str):
        self.username = username
        self.hashed_password = hashed_password


# Criando uma instância da "base de dados"
some_database = SomeDatabase()

app = FastAPI(title="apidovincenzo  ")

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['pessoasdb']
collection = db['pessoas']

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = "user"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model
class User(BaseModel):
    username: str
    email: Optional[str] = None

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# TokenData model for dependency
class TokenData(BaseModel):
    username: Optional[str] = None

# Dependency function to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Model for creating a new person
class PessoaCreate(BaseModel):
    apelido: str
    nome: str
    nascimento: str
    stack: Optional[List[str]] = None

    class Config:
        max_anystr_length = 32
# Model for response
class PessoaResponse(BaseModel):
    id: str
    apelido: str
    nome: str
    nascimento: int
    stack: Optional[List[str]] = None

# Função fictícia para autenticar o usuário
def authenticate_user(username: str, password: str):
    user = some_database.get_user(username)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

# Função fictícia para criar um token JWT
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoint to create a new person, requires authentication
@app.post('/pessoas', response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def create_pessoa(pessoa: PessoaCreate, current_user: str = Depends(get_current_user)):
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

# Endpoint to retrieve a person by ID
@app.get('/pessoas/{id}', response_model=PessoaResponse)
async def find_by_id(id: str, current_user: str = Depends(get_current_user)):
    pessoa = collection.find_one({'id': id})
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return pessoa

# Endpoint to search for people by term (apelido, nome, or stack)
@app.get('/pessoas', response_model=list[PessoaResponse])
def find_by_term(term: str = Query(..., min_length=1), current_user: str = Depends(get_current_user)):
    results = []
    cursor = collection.find()
    for pessoa in cursor:
        if term.lower() in pessoa['apelido'].lower() or term.lower() in pessoa['nome'].lower() or (pessoa['stack'] and any(term.lower() in stack_item.lower() for stack_item in pessoa['stack'])):
            results.append(pessoa)
    return results

# Endpoint to count people
@app.get("/contagem-pessoas")
def count_pessoas(current_user: str = Depends(get_current_user)):
    count = collection.count_documents({})
    return count

# Endpoint para obter token usando o fluxo de concessão de senha (password grant type)
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}