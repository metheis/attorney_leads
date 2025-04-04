from sqlmodel import Field, SQLModel

class CandidateBase(SQLModel):
    full_name: str = Field(index=True)
    resume_file: str | None = None

class Candidate(CandidateBase, table=True):
    email: str | None = Field(default=None, primary_key=True)
    status: str | None = "PENDING "

class CandidateUpdate(CandidateBase):
    full_name: str 
    resume_file: str | None = None

class CandidateUpdateAttorney(CandidateUpdate):
    status: str | None = "REACHED_OUT"

class AttorneyBase(SQLModel):
    full_name: str
    email: str
    username: str | None = Field(default=None, primary_key=True)

class Attorney(AttorneyBase, table=True):
    hashed_password: str
    id: int | None = Field(default=None)

class AttorneyCreate(AttorneyBase):
    password: str | None = None
