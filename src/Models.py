from pydantic import BaseModel
from typing import List, Optional
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
    verified: Optional[bool] = None
    verification_comment: str = ""
    verification_output: Optional[Prescription] = None
    approved: Optional[bool] = None
    approval_comment: str = ""

class PrescriptionData(Basemodel):
    student_username: str
    rest_duration: int
    scan_img: bytearray
    def __str__(self):
        return self.student_username + str(self.rest_duration) + '.' + str(self.scan_img)

class Prescription(Basemodel):
    student_username: str
    rest_duration: int
    scan_img: bytearray
    signature: str
    def __str__(self):
        return self.student_username + str(self.rest_duration) + '.' + str(self.scan_img) + '.' + self.signature
    def get_data_str(self):
        return self.student_username + str(self.rest_duration) + '.' + str(self.scan_img)

class Block(BaseModel):
    index: int
    timestamp: date
    data: Prescription
    nonce: int
    previous_hash: str

class BlockData(BaseModel):
    index: int
    timestamp: date