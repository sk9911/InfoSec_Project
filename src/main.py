from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from Models import User, UserLogin, UserView, Makeup, MakupData, Request, RequestData
import blockchain as _blockchain
import Database as _database
import UserDatabase as _userDatabase

import jwt
import json as _json
from datetime import datetime, timedelta

blockchain = _blockchain.Blockchain()
makeupDB = _database.Database()
userDB = _userDatabase.UserDatabase()

JWT_SECRET = "thisisthejwtsecretformedcserver"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='signin')

app = FastAPI()

################################################# User Endpoints #################################################
@app.post('/signup', response_model=User)
def create_new_user(form_data: User):
    print("SIGNUP REQ",form_data)
    new_user = userDB.create(user=form_data)
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    print("SIGNUP RES", new_user)
    return new_user

@app.post('/signin')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = userDB.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    token = jwt.encode(user.dict(), JWT_SECRET)
    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user = userDB.read(username=payload.get('username'))
    if not user:
        raise HTTPException(status_code=401, detail='Not Authorized')
    return user

@app.get('/me', response_model=UserView)
async def get_user(user: UserView = Depends(get_current_user)):
    return user    

################################################ Makeup Endpoints ################################################


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
