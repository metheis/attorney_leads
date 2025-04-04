# db.py

from fastapi import Depends, HTTPException
from sqlmodel import create_engine, Session, select
from models import *


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """
    Create the database and tables.
    """
    SQLModel.metadata.create_all(engine)

def create_db_candidate(candidate: Candidate):
    """
    Create a new candidate in the database.
    """
    with Session(engine) as session:
        existing_candidate = session.get(Candidate, candidate.email)
        if existing_candidate:
            return existing_candidate
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        return candidate
    
def read_db_candidate(email: str):
    """
    Read a candidate from the database by email.
    """
    with Session(engine) as session:
        db_candidate = session.get(Candidate, email)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Email not found")
        return db_candidate
    
def update_db_candidate(email: str, update_candidate: CandidateUpdate):
    """
    Update a candidate's information in the database by email.
    """
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
    """
    Get all candidates from the database.
    """
    with Session(engine) as session:
        statement = select(Candidate)
        results = session.exec(statement).all()
        return results
    
def create_db_attorney(attorney: Attorney):
    """
    Create a new attorney in the database.
    """
    with Session(engine) as session:
        existing_attorney = session.get(Attorney, attorney.username)
        if existing_attorney:
            return existing_attorney
        session.add(attorney)
        session.commit()
        session.refresh(attorney)
        return attorney
    
def auth_db_attorney(username: str):
    """
    Authenticate an attorney by username. Return the attorney object if found.
    """
    with Session(engine) as session:
        db_attorney = session.get(Attorney, username)
        if not db_attorney:
            raise HTTPException(status_code=404, detail="Incorrect username or password")
        return db_attorney
    

