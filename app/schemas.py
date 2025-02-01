from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# USERS
class UserModel(BaseModel):
    uid: uuid.UUID
    email: str
    password: str 
    first_name: str
    last_name: str
    phone_number: str
    exam_centre_no: str 
    exam_id: str

class UserCreateModel(BaseModel):
    email: str
    password: str 
    first_name: str
    last_name: str

class UserResponseModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    exam_centre_no: Optional[str] = None
    exam_id: Optional[str] = None
    is_verified: bool
    is_paid: bool

class UserLoginModel(BaseModel):
    email: str
    password: str 


# STUDENTS
class Student(BaseModel):
    uid: uuid.UUID 
    first_name: str
    last_name: str
    exam_centre_no: str 
    exam_id: str
    exam_year: int
    result: dict
    created_at: datetime 
    updated_at: datetime

class StudentCreateModel(BaseModel):
    first_name: str
    last_name: str
    exam_centre_no: str 
    exam_year: int
    result: Optional[dict] = None

class StudentResponseModel(BaseModel):
    first_name: str
    last_name: str
    exam_centre_no: str 
    exam_id: str
    exam_year: int
    result: Optional[dict] = None
    exam_centre: Optional['ExamCentreProfileModel']

# CENTRES

class ExamCentre(BaseModel):
    uid: uuid.UUID
    exam_centre_no: str
    exam_centre_name: str
    exam_centre_location: str
    exam_centre_admin: str
    exam_centre_admin_email: str
    exam_centre_admin_phone: str
    created_at: datetime
    updated_at: datetime
    
class ExamCentreCreateModel(BaseModel):
    exam_centre_name: str
    exam_centre_location: str
    exam_centre_admin: str
    exam_centre_admin_email: str
    exam_centre_admin_phone: str

class ExamCentreProfileModel(BaseModel):
    exam_centre_no: str
    exam_centre_name: str

class ExamCentreResponseModel(ExamCentre):
    students: List['StudentResponseModel']

  
# ADMIN
class Admin(BaseModel):
    uid: uuid.UUID 
    email: str
    password: str = Field(exclude=True)
    first_name: str
    last_name: str
    phone_number: str
    is_verified: bool = False
    created_at: datetime 
    updated_at: datetime 

class AdminCreateModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str

class AdminLoginModel(BaseModel):
    email: str
    password: str 

class AdminResponseModel(BaseModel):
    email: str
    first_name: str

class AdminProfileModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str


# TOKEN

class RevokedTokenModel(BaseModel):
    token_jti: str


# EMAIL MODELS

class EmailModel(BaseModel):
    addresses: List[str]


# SUBJECTS

class Subject(BaseModel):
    uid: uuid.UUID
    subject_code: str
    subject_name: str
    created_at: datetime
    updated_at: datetime

class SubjectCreateModel(BaseModel):
    subject_name: str

class SubjectResModel(BaseModel):
    subject_name: str
    subject_code: str

class SubjectResponseModel(SubjectResModel):
    uid: uuid.UUID

# RESULT DATA
