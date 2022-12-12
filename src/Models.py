from pydantic import BaseModel
from typing import List, Optional, Union
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
    token: Optional[str] = None

class MakeupData(BaseModel):
    title: str
    eval_date: date

class Makeup(BaseModel):
    id: int
    professor: UserView
    title: str
    eval_date: date
    isOpen: bool = True

class Prescription(BaseModel):
    student_username: str
    rest_duration: int
    scan_img: str
    img_hash: str
    signature: Optional[str] = None
    def get_data_str(self):
        return self.student_username + str(self.rest_duration) + self.scan_img + self.img_hash

class MRequestData(BaseModel):
    block_index: int
    makeup_id: int

class MRequest(BaseModel):
    id: int
    student: UserView
    block_index: int
    makeup: Makeup
    verified: Optional[bool] = None
    verification_comment: str = "Verification Pending"
    verification_output: Optional[Prescription] = None
    approved: Optional[bool] = None
    approval_comment: str = "Approval Pending"

class Block(BaseModel):
    index: int
    timestamp: date
    data: Union[Prescription,None]
    nonce: int
    previous_hash: str

class BlockData(BaseModel):
    index: int
    timestamp: date