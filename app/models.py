from sqlmodel import SQLModel, Field, Column, String, Relationship, Text
from datetime import datetime, timezone
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import Optional, List


# USERS
class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False) 
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    phone_number: str = Field(nullable=True)
    exam_centre_no: str = Field(foreign_key="exam_centres.exam_centre_no", nullable=True) 
    exam_id: str = Field(nullable=True, unique=True)
    role: str = Field(nullable=False, default="user")
    is_verified: bool = Field(default=False)
    is_paid: bool = Field(default=False)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))
    

    def __repr__(self):
        return f"<User {self.first_name}>"

# STUDENTS
class Student(SQLModel, table=True):
    __tablename__ = "students"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    exam_centre_no: str = Field(foreign_key="exam_centres.exam_centre_no", nullable=False) 
    exam_id: str = Field(nullable=False)
    is_approved: bool = Field(default=False)
    exam_year: int = Field(nullable=False)
    result: Optional[dict] = Field(sa_column=Column("result", pg.JSONB(astext_type=Text())))
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))
    exam_centre: Optional['ExamCentre'] = Relationship(back_populates="students", sa_relationship_kwargs={"lazy":"selectin"})

    def __repr__(self):
        return f"<Result {self.uid}>"

# EXAM_CENTRES
class ExamCentre(SQLModel, table=True):
    __tablename__ = "exam_centres"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    exam_centre_no: str = Field(nullable=False, unique=True)
    exam_centre_name: str = Field(nullable=False, unique=True)
    exam_centre_location: str = Field(nullable=False)
    exam_centre_admin: str = Field(nullable=False)
    exam_centre_admin_email: str = Field(nullable=False, unique=True)
    exam_centre_admin_phone: str = Field(nullable=False)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))
    students: List['Student'] = Relationship(back_populates="exam_centre", sa_relationship_kwargs={"lazy":"selectin"})

    def __repr__(self):
        return f"<exam_centre {self.exam_centre_name}>"


# ADMIN
class Admin(SQLModel, table=True):
    __tablename__ = "admins"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False) 
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    phone_number: str = Field(nullable=False)
    role: str = Field(nullable=False, default="admin")
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Admin {self.first_name}>"

# TOKEN
class RevokedToken(SQLModel, table=True):
    __tablename__="revokedtoken"
    tokenid: uuid.UUID = Field(
        sa_column= Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    token_jti : str = Field(sa_column= Column(String(300), primary_key=True))

    def __repr__(self):
        return f"<Token {self.token_jti}>"
    
# SUBJECTS

class Subject(SQLModel, table=True):
    __tablename__ = "subjects"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subject_name: str = Field(nullable=False)
    subject_code: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now, nullable=False))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Subject {self.subject_name}>"