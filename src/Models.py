from pydantic import BaseModel
from typing import List, Union
from enum import Enum
from datetime import date

class UserLogin(BaseModel):
    username: str
    password: str

class UserAccount(Enum):
    Doctor = "Doctor"
    Professor = "Professor"
    Student = "Student"

class UserView(BaseModel):
    username: str
    account: UserAccount
    class Config:  
        use_enum_values = True

class User(BaseModel):
    username: str
    password: str
    account: UserAccount

class MakeupData(BaseModel):
    title: str
    eval_date: date

class Makeup(BaseModel):
    id: int
    professor: UserView
    title: str
    eval_date: date
    isOpen: bool = True

class RequestData(BaseModel):
    block_index: int
    makeup_id: int

class Request(BaseModel):
    id: int
    student: UserView
    block_index: int
    makeup: Makeup
    verification: Union[bool,None] = None
    approval: Union[bool,None] = None