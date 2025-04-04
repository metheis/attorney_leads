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
    """
    Create a new candidate and send a confirmation email.
    The candidate's email address is validated before sending the email.
    If the candidate already exists, the existing candidate is returned.
    """
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
    """
    Retrieve a candidate by their email address.
    """
    candidate = read_db_candidate(email)
    if candidate:
        return candidate
    else:
        return {"message": "Candidate not found"}
    
@app.patch("/candidate/{email}", response_model=Candidate)
def update_candidate(
    email: str, candidate: CandidateUpdate
):
    """
    Update a candidate's information by their email address.
    """
    return update_db_candidate(email, candidate)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """
    Upload a file and save it to the server.
    The file is saved in the "resumes" directory with its original filename.
    """
    contents = await file.read()
    with open(f"resumes/{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}

"""Template Authentication Helpers"""

def fake_hash_password(password: str):
    # This doesn't provide any security at all
    # Don't use this in production!
    return "fakehashed" + password

def get_auth_user(username: str):
    # This doesn't provide any security at all
    # Don't use this in production!
    return auth_db_attorney(username)

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Don't use this in production!
    user = get_auth_user(token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # Simulate a user authentication process.
    # In a real application, you would verify the token and get the user from the database.
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
    """
    Create a new attorney user with hashed password.
    The attorney's email address is validated before creating the user.
    Another attorney's auth token is used to authenticate the request.
    """
    if not val_address(attorney.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    hashed_password = fake_hash_password(attorney.password)
    val_attorney = Attorney(**attorney.model_dump(exclude={"password"}), hashed_password=hashed_password)
    return create_db_attorney(val_attorney)

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """"
    Authentication for attorney users.
    The attorney's username and password are validated against the database.
    """
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
    """
    Retrieve all candidates for the authenticated attorney user.
    The attorney's auth token is used to authenticate the request.
    """
    if current_user:
        return get_all_candidates()
    
@app.patch("/attorney/candidate/{email}", response_model=Candidate)
def update_candidate_attorney(
    current_user: Annotated[AttorneyBase, Depends(get_current_user)],
    email: str, candidate: CandidateUpdateAttorney
):
    """
    Update a candidate's information (specifically their status) by their email address.
    The attorney's auth token is used to authenticate the request.
    """
    return update_db_candidate(email, candidate)

