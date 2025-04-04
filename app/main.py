# main.py

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, UploadFile, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from typing import Annotated

from models import Candidate, CandidateUpdate, CandidateUpdateAttorney, Attorney, AttorneyBase, AttorneyCreate
from db import create_db_and_tables, create_db_candidate, read_db_candidate, get_all_candidates, update_db_candidate, create_db_attorney, auth_db_attorney
from simple_mail import simple_send_candidate, simple_send_attorney, val_address

default_admin = {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@company.com",
        "hashed_password": "fakehashedsecret",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database and tables if they do not exist
    if not os.path.exists("database.db"):
        create_db_and_tables()
        create_db_attorney(Attorney(**default_admin))
    yield

app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def default():
    return {"message": "Please use /docs to see the API documentation"}

"""Candidate API"""

@app.post("/candidate/")
async def create_candidate(candidate: Candidate):
    if not val_address(candidate.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    db_candidate = create_db_candidate(candidate)
    if db_candidate:
        # Send email to candidate
        await simple_send_candidate(db_candidate.email, db_candidate.full_name)
        # Send email to the default admin attorney, current just the admin
        attorney = auth_db_attorney("admin")
        await simple_send_attorney(attorney.email, attorney.full_name, db_candidate.full_name)
        return db_candidate
    else:
        return {"message": "Failed to create candidate"}

@app.get("/candidate/{email}")
def read_candidate(email: str):
    candidate = read_db_candidate(email)
    if candidate:
        return candidate
    else:
        return {"message": "Candidate not found"}
    
@app.patch("/candidate/{email}", response_model=Candidate)
def update_candidate(
    email: str, candidate: CandidateUpdate
):
    return update_db_candidate(email, candidate)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    with open(f"resumes/{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}

"""Template Authentication Helpers"""

def fake_hash_password(password: str):
    return "fakehashed" + password

def get_auth_user(username: str):
    return auth_db_attorney(username)

def fake_decode_token(token):
    # This doesn't provide any security at all
    user = get_auth_user(token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

"""Attorney API"""

@app.post("/attorney/create")
async def create_attorney(current_user: Annotated[AttorneyBase, Depends(get_current_user)], attorney: AttorneyCreate):
    if not val_address(attorney.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    hashed_password = fake_hash_password(attorney.password)
    val_attorney = Attorney(**attorney.model_dump(exclude={"password"}), hashed_password=hashed_password)
    return create_db_attorney(val_attorney)

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Simulate authentication.
    db_attorney = auth_db_attorney(form_data.username)
    if (db_attorney):
        hashed_password = fake_hash_password(form_data.password)
        if not hashed_password == db_attorney.hashed_password:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": db_attorney.username, "token_type": "bearer"}

@app.get("/attorney/leads")
async def load_attorney_leads(
    current_user: Annotated[AttorneyBase, Depends(get_current_user)],
):
    if current_user:
        return get_all_candidates()
    
@app.patch("/attorney/candidate/{email}", response_model=Candidate)
def update_candidate_attorney(
    current_user: Annotated[AttorneyBase, Depends(get_current_user)],
    email: str, candidate: CandidateUpdateAttorney
):
    return update_db_candidate(email, candidate)

