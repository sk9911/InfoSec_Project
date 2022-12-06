from pydantic import BaseModel
from typing import List, Union
from enum import Enum
from datetime import date

class UserLogin(BaseModel):
    username: str
    password: str

class UserAccount(Enum):
    Doctor = 1
    Professor = 2
    Student = 3

class UserView(BaseModel):
    username: str
    account: UserAccount
    class Config:  
        use_enum_values = True

class User(BaseModel):
    username: str
    password: str
    account: UserAccount

class MakupData(BaseModel):
    professor_username: str
    title: str
    eval_date: date

class Makeup(BaseModel):
    id: int
    professor: User
    title: str
    eval_date: date
    status: Enum('MakeupStatus', ["Open","Closed","Published","Archived"]) = 0
    request_ids: List[int] = []

class RequestData(BaseModel):
    student_username: str
    block_index: int

class Request(BaseModel):
    id: int
    student: User
    block_index: int
    verification: Union[bool,None] = None
    status: Enum('RequestStatus',["Pending","Approved","Rejected"]) = 0