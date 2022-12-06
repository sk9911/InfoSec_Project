from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from Models import User, UserAccount, UserLogin, UserView, Makeup, MakeupData, Request, RequestData
from Blockchain import Blockchain
from Database import MakeupDatabase, RequestDatabase, UserDatabase

import jwt
import json as _json
from datetime import datetime, timedelta
from typing import List

blockchain = Blockchain()
makeupDB = MakeupDatabase()
requestDB = RequestDatabase()
userDB = UserDatabase()

JWT_SECRET = "thisisthejwtsecretformedcserver"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='signin')

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
    print("MIDDLEWARE", user.account, UserAccount.Professor)
    if user.account != UserAccount.Professor.value:
        raise HTTPException(status_code=401, detail='Invalid Account Type')
    else:
        return user
def get_current_stud(user:UserView = Depends(get_current_user)):
    if user.account != UserAccount.Student.value:
        raise HTTPException(status_code=401, detail='Invalid Account Type')
    else:
        return user

################################################# User Endpoints #################################################
@app.get('/users', response_model=List[str])
def get_all_users():
    return userDB.get_all()

@app.post('/signup', response_model=User)
def create_new_user(form_data: User):
    # print("SIGNUP REQ",form_data)
    new_user = userDB.create(user=form_data)
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    # print("SIGNUP RES", new_user)
    return new_user

@app.post('/signin')
def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = userDB.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    token = jwt.encode(user.dict(), JWT_SECRET)
    return {'access_token' : token, 'token_type' : 'bearer'}

@app.get('/me', response_model=UserView)
def get_user(user: UserView = Depends(get_current_user)):
    return user    

################################################ Makeup Endpoints ################################################
@app.get('/makeup', response_model=List[Makeup])
def get_all_makeups():
    return makeupDB.get_all()

@app.post('/makeup', response_model=Makeup)
def create_new_makeup(form_data: MakeupData, prof: UserView = Depends(get_current_prof)):
    new_makeup = Makeup(
        id = makeupDB.size(),
        professor = prof,
        title = form_data.title,
        eval_date = form_data.eval_date,
    )
    res = makeupDB.create(new_makeup)
    return res

@app.put('/makeup/{makeup_id}/edit', response_model=Makeup)
def edit_makeup(makeup_id:int, form_data: MakeupData, prof: UserView = Depends(get_current_prof)):
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
def close_makeup(makeup_id:int, prof: UserView = Depends(get_current_prof)):
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
def create_new_request(form_data: RequestData, stud: UserView = Depends(get_current_stud)):
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
def edit_request(request_id:int, block_index: int, stud: UserView = Depends(get_current_stud)):
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

############################################## Blockchain Endpoints ##############################################
# endpoint to submit visitation document
@app.post("/add_visit/")
def mine_block(visit_doc: str):
    if not blockchain.is_chain_valid():
        return HTTPException(status_code=400, detail="The blockchain is invalid")
    
    # visit_doc contains
    ## student_id : string
    ## issue_scale : number #(1,2,3,4,5)
    ## rest_duration : number #(nos of days)
    block = blockchain.mine_block(data=visit_doc)
    return {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "data": block["data"]
    }

############################################## Verification Endpoints ##############################################
# endpoint to verify request document
@app.post("/verify_makeups/")
def verify_visitation(verif_doc: str):
    # verif doc contains
    ## eval_date : string #("dd-mm-YYYY")
    ## issue_threshold : number #(1,2,3,4,5)
    ## makeup_reqs : [ {
    #### student_id : string
    #### block_index : number
    ## } ]

    doc = _json.loads(verif_doc)
    makeup_approved = []
    makeup_rejected = []
    for req in doc['makeup_reqs']:
        block = blockchain.get_block_from_index(req['block_index'])
        if block != None: data = _json.loads(block["data"])

        if block == None:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Block not found"
                })
        elif data['student_id'] != req["student_id"]:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Student ID mismatch"
                })
        elif data['issue_scale'] < doc['issue_threshold']:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Low scale of Health Issue"
                })
        elif datetime.strptime(doc['eval_date'],"%d-%m-%Y") - datetime.strptime(block['timestamp'],"%d-%m-%Y") > timedelta(days=data['rest_duration']):
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Evaluation not in Rest period"
                })
        else:
            makeup_approved.append({"student_id": req["student_id"]})
    
    return { "approved":makeup_approved, "rejected":makeup_rejected }

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
