from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List
import jwt

from Models import User, UserAccount, UserLogin, UserView, Makeup, MakeupData, Request, RequestData, Prescription, BlockData
from Blockchain import Blockchain
from Database import MakeupDatabase, RequestDatabase, UserDatabase
from Cryptography import Cryptography

blockchain = Blockchain()
makeupDB = MakeupDatabase()
requestDB = RequestDatabase()
userDB = UserDatabase()
crypto = Cryptography()

JWT_SECRET = "thisisthejwtsecretformakeupsystem"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='signin')

templates = Jinja2Templates(directory="templates")

app = FastAPI()

################################################# Auth Middleware ################################################
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = userDB.read(username=payload.get('username'))
    if not user:
        raise HTTPException(status_code=401, detail='Not Authorized')
    return user
def get_current_doc(user:User = Depends(get_current_user)):
    if user.account != UserAccount.Doctor.value:
        raise HTTPException(status_code=401, detail='Invalid Account Type')
    else:
        return user
def get_current_prof(user:User = Depends(get_current_user)):
    # print("MIDDLEWARE", user.account, UserAccount.Professor)
    if user.account != UserAccount.Professor.value:
        raise HTTPException(status_code=401, detail='Invalid Account Type')
    else:
        return user
def get_current_stud(user:UserView = Depends(get_current_user)):
    if user.account != UserAccount.Student.value:
        raise HTTPException(status_code=401, detail='Invalid Account Type')
    else:
        return user

################################################# HTML Endpoints #################################################
@app.get("/home", response_class=HTMLResponse)
async def read(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

################################################# User Endpoints #################################################
@app.get('/users', response_model=List[User])
def get_all_users():
    return userDB.get_all()


@app.post('/signup/doc', response_model=User)
async def create_new_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # print("SIGNUP REQ",form_data)
    new_user = userDB.create(User(
        username = form_data.username,
        password = form_data.password,
        account = UserAccount.Doctor
    ))
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    return new_user

@app.post('/signup/prof', response_model=User)
async def create_new_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # print("SIGNUP REQ",form_data)
    new_user = userDB.create(User(
        username = form_data.username,
        password = form_data.password,
        account = UserAccount.Professor
    ))
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    return new_user

@app.post('/signup/stud', response_model=User)
async def create_new_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # print("SIGNUP REQ",form_data)
    new_user = userDB.create(User(
        username = form_data.username,
        password = form_data.password,
        account = UserAccount.Student
    ))
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    return new_user

@app.post('/signin')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = userDB.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials') 
    token = userDB.giveToken(user.username, jwt.encode({"username":user.username, "timestamp":datetime.now().timestamp()}, JWT_SECRET))
    return {'access_token' : token, 'token_type' : 'bearer'}

@app.get('/signout')
def get_user(uv: UserView = Depends(get_current_user)):
    userDB.takeToken(uv.username)
    return True    

@app.get('/me', response_model=User)
def get_user(uv: UserView = Depends(get_current_user)):
    user = userDB.read(uv.username)
    return user

################################################ Makeup Endpoints ################################################
@app.get('/makeup', response_model=List[Makeup])
def get_all_makeups():
    return makeupDB.get_all()

@app.post('/makeup', response_model=Makeup)
async def create_new_makeup(form_data: MakeupData = Form(...), prof: UserView = Depends(get_current_prof)):
    new_makeup = Makeup(
        id = makeupDB.size(),
        professor = prof,
        title = form_data.title,
        eval_date = form_data.eval_date,
    )
    res = makeupDB.create(new_makeup)
    return res

@app.put('/makeup/{makeup_id}/edit', response_model=Makeup)
async def edit_makeup(makeup_id:int, form_data: MakeupData = Form(...), prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_makeup = Makeup(
        id = makeup_id,
        professor = prof,
        title = form_data.title,
        eval_date = form_data.eval_date,
    )
    res = makeupDB.update(makeup_id,updated_makeup)
    return res

@app.get('/makeup/{makeup_id}/close', response_model=Makeup)
async def close_makeup(makeup_id:int, prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    res = makeupDB.close_makeup(makeup_id)
    return res

@app.get('/makeup/prof', response_model=List[Makeup])
def get_prof_makeups(prof: UserView = Depends(get_current_prof)):
    return makeupDB.get_prof(prof.username)

@app.get('/makeup/open', response_model=List[Makeup])
def get_open_makeups(prof: UserView = Depends(get_current_stud)):
    return makeupDB.get_open()

################################################ Request Endpoints ###############################################
@app.get('/request', response_model=List[Request])
def get_all_requests():
    return requestDB.get_all()

@app.post('/request', response_model=Request)
async def create_new_request(form_data: RequestData = Form(...), stud: UserView = Depends(get_current_stud)):
    original_makeup = makeupDB.read(form_data.makeup_id)
    if not original_makeup or not original_makeup.isOpen:
        raise HTTPException(status_code=404, detail='Not Found')
    new_request = Request(
        id = requestDB.size(),
        student = stud,
        block_index = form_data.block_index,
        makeup = makeupDB.read(form_data.makeup_id),
    )
    res = requestDB.create(new_request)
    return res

@app.put('/request/{request_id}/edit', response_model=Request)
async def edit_request(request_id:int, block_index: int = Form(...), stud: UserView = Depends(get_current_stud)):
    original_request = requestDB.read(request_id)
    if not original_request:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_request.student.username != stud.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    updated_request = Request(
        id = original_request.id,
        student = stud,
        block_index = block_index,
        makeup = original_request.makeup,
    )
    res = requestDB.update(request_id,updated_request)
    return res

@app.get('/request/stud', response_model=List[Request])
def get_stud_requests(stud: UserView = Depends(get_current_stud)):
    return requestDB.get_student(stud.username)

@app.get('/request/prof/{makeup_id}', response_model=List[Request])
def get_stud_requests(makeup_id:int, prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    return requestDB.get_makeup(makeup_id)

############################################# Prescription Endpoints #############################################
# endpoint to submit visitation document
@app.post("/prescription", response_model=BlockData)
async def mine_block(student_username:str = Form(...), rest_duration:int = Form(...), scan_img:bytes = Form(...), doc: UserView = Depends(get_current_doc)):
    if not blockchain.is_chain_valid():
        return HTTPException(status_code=400, detail="Blockchain is Invalid")
    message = student_username + str(rest_duration) + '.' + str(scan_img)
    prescription = Prescription(
        student_username = student_username,
        rest_duration = rest_duration,
        scan_img = scan_img,
        signature = crypto.sign_message(message)
    )
    block = blockchain.mine_block(data=prescription)
    return BlockData(index=block.index, timestamp=block.timestamp)

####################################### Verification and Approval Endpoints ######################################
# endpoint to verify request document
@app.post("/request/verify")
async def verify_visitation(req_ids: List[int] = Form(...), prof: UserView = Depends(get_current_prof)):
    for req_id in req_ids:
        req: Request = requestDB.read(req_id)
        if not req:
            continue

        block = blockchain.get_block_from_index(req.block_index)
        if not block:
            req.verified = False
            req.verification_comment = "Prescription Not Found"
            requestDB.update(req_id, req)
        
        elif req.student.username != block.data.student_username:
            req.verified = False
            req.verification_comment = "Student Username Did Not Match"
            requestDB.update(req_id, req)

        # Signature Verification
        elif not crypto.verify_signature(block.data.get_data_str(), block.data.signature):
            req.verified = False
            req.verification_comment = "Signature Verification Failed"
            req.verification_output = block.data
            requestDB.update(req_id, req)

        elif req.makeup.eval_date - block.timestamp > timedelta(days=block.data.rest_duration):
            req.verified = False
            req.verification_comment = "Evaluation Date Not In Rest period"
            req.verification_output = block.data
            requestDB.update(req_id, req)

        else:
            req.verified = True
            req.verification_comment = "Verified"
            req.verification_output = block.data
            requestDB.update(req_id, req)
    
    return True

@app.put('/request/{request_id}/approve', response_model=Request)
async def edit_request(request_id:int, value: bool = Form(...), comment: str = Form(...), prof: UserView = Depends(get_current_prof)):
    req = requestDB.read(request_id)
    if not req:
        raise HTTPException(status_code=404, detail='Not Found')
    if req.makeup.prof_username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    
    req.approved = value
    req.approval_comment = comment
    req = requestDB.update(request_id,req)
    return req

################################################# Test Endpoints #################################################
# endpoint to return the entire blockchain
@app.get("/test/blockchain/")
def get_blockchain():
    if not blockchain.is_chain_valid():
        return HTTPException(status_code=400, detail="The blockchain is invalid")
    chain = blockchain.chain
    return chain

# endpoint to check if the chain is valid
@app.get("/test/validate/")
def is_blockchain_valid():
    if not blockchain.is_chain_valid():
        return HTTPException(status_code=400, detail="The blockchain is invalid")

    return blockchain.is_chain_valid()
