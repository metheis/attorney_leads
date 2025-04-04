from sqlmodel import Field, SQLModel

class CandidateBase(SQLModel):
    """
    Base model for candidates.
    """
    full_name: str = Field(index=True)
    resume_file: str | None = None

class Candidate(CandidateBase, table=True):
    """
    Model for candidates in the database.
    """
    email: str | None = Field(default=None, primary_key=True)
    status: str | None = "PENDING "

class CandidateUpdate(CandidateBase):
    """
    Model for updating candidate information.
    """
    full_name: str 
    resume_file: str | None = None

class CandidateUpdateAttorney(CandidateUpdate):
    """
    Model for updating candidate information by attorney.
    """
    status: str | None = "REACHED_OUT"

class AttorneyBase(SQLModel):
    """
    Base model for attorneys.
    """
    full_name: str
    email: str
    username: str | None = Field(default=None, primary_key=True)

class Attorney(AttorneyBase, table=True):
    """
    Model for attorneys in the database.
    """
    hashed_password: str
    id: int | None = Field(default=None)

class AttorneyCreate(AttorneyBase):
    """
    Model for creating a new attorney.
    """
    password: str | None = None
