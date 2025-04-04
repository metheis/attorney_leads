# db.py

from fastapi import Depends, HTTPException
from sqlmodel import create_engine, Session, select
from models import *


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def create_db_candidate(candidate: Candidate):
    with Session(engine) as session:
        existing_candidate = session.get(Candidate, candidate.email)
        if existing_candidate:
            return existing_candidate
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate
    
def read_db_candidate(email: str):
    with Session(engine) as session:
        db_candidate = session.get(Candidate, email)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Email not found")
        return db_candidate
    
def update_db_candidate(email: str, update_candidate: CandidateUpdate):
    with Session(engine) as session:
        db_candidate = session.get(Candidate, email)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Email not found")
        candidate_data = update_candidate.model_dump(exclude_unset=True)
        for key, value in candidate_data.items():
            setattr(db_candidate, key, value)
        session.add(db_candidate)
        session.commit()
        session.refresh(db_candidate)
        return db_candidate
    
def get_all_candidates():
    with Session(engine) as session:
        statement = select(Candidate)
        results = session.exec(statement).all()
        return results
    
def create_db_attorney(attorney: Attorney):
    with Session(engine) as session:
        existing_attorney = session.get(Attorney, attorney.username)
        if existing_attorney:
            return existing_attorney
        session.add(attorney)
        session.commit()
        session.refresh(attorney)
        return attorney
    
def auth_db_attorney(username: str):
    with Session(engine) as session:
        db_attorney = session.get(Attorney, username)
        if not db_attorney:
            raise HTTPException(status_code=404, detail="Incorrect username or password")
        return db_attorney
    

