from fastapi import FastAPI, Request, Response
from fastapi import HTTPException, Depends, Form, Cookie, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import datetime, timedelta
from typing import List
import jwt
import hashlib

from Models import User, UserAccount, UserLogin, UserView, Makeup, MakeupData, MRequest, MRequestData, Prescription, BlockData
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

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

################################################# Auth Middleware ################################################
def get_current_user(access_token: str = Cookie(default=None)):
    # print("TOKEN",access_token)
    token = access_token.split(" ")[-1]
    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    # print("PAYLOAD",payload)
    user = userDB.read(username=payload.get('username'))
    # print("USER", user)
    if not user:
        raise HTTPException(status_code=401, detail='MKC')
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
@app.get("/", response_class=HTMLResponse)
async def show_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def show_signup(request: Request, account_type:str):
    accounts = {
        "doc": "Doctor",
        "prof": "Professor",
        "stud": "Student"
    }
    return templates.TemplateResponse("signup.html", {"request": request, "account_type":account_type, "account_name":accounts[account_type]})

@app.get("/signin", response_class=HTMLResponse)
async def show_signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get("/stud", response_class=HTMLResponse)
async def show_stud(request: Request, uv:UserView = Depends(get_current_stud)):
    return templates.TemplateResponse("stud.html", {"request": request, "user":uv, "student_requests":get_stud_requests(uv), "open_makeups":get_open_makeups(uv) })

@app.get("/prof", response_class=HTMLResponse)
async def show_prof(request: Request, uv:UserView = Depends(get_current_prof)):
    return templates.TemplateResponse("prof.html", {"request": request, "user":uv, "prof_makeups":get_prof_makeups(uv)})

@app.get("/doc", response_class=HTMLResponse)
async def show_doc(request: Request, uv:UserView = Depends(get_current_doc)):
    return templates.TemplateResponse("doc.html", {"request": request, "user":uv})

################################################# User Endpoints #################################################
@app.get('/users', response_model=List[User])
def get_all_users():
    return userDB.get_all()


@app.post('/signup', response_class=RedirectResponse)
async def create_new_user(account_type: str, form_data: OAuth2PasswordRequestForm = Depends()):
    accounts = {
        "doc": UserAccount.Doctor,
        "prof": UserAccount.Professor,
        "stud": UserAccount.Student
    }
    new_user = userDB.create(User(
        username = form_data.username,
        password = form_data.password,
        account = accounts[account_type]
    ))
    if not new_user:
        raise HTTPException(status_code=401, detail='Username Already Exists')
    return "/signin"

@app.post('/token')
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(oauth2_scheme)):
    user = userDB.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials') 
    token = userDB.giveToken(user.username, jwt.encode({"username":user.username, "timestamp":datetime.now().timestamp()}, JWT_SECRET))
    return {'access_token' : token, 'token_type' : 'bearer'}

@app.post('/signin', response_class=HTMLResponse)
async def signin_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = userDB.authenticate(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials') 
    token = userDB.giveToken(user.username, jwt.encode({"username":user.username, "timestamp":datetime.now().timestamp()}, JWT_SECRET))
    
    if user.account.value == "Doctor":
        response = templates.TemplateResponse("doc.html", {"request": request, "user":user})
    elif user.account.value == "Professor":
        response = templates.TemplateResponse("prof.html", {"request": request, "user":user, "prof_makeups":get_prof_makeups(user)})
    elif user.account.value == "Student":
        response = templates.TemplateResponse("stud.html", {"request": request, "user":user, "student_requests":get_stud_requests(user), "open_makeups":get_open_makeups(user) })

    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@app.get('/signout', response_class=RedirectResponse)
def get_user(uv: UserView = Depends(get_current_user)):
    userDB.takeToken(uv.username)
    return "/"    

################################################ Makeup Endpoints ################################################
@app.get('/makeup', response_model=List[Makeup])
def get_all_makeups():
    return makeupDB.get_all()

@app.post('/makeup', response_class=HTMLResponse)
def create_new_makeup(request:Request, title:str = Form(...), eval_date:str = Form(...), prof: UserView = Depends(get_current_prof)):
    new_makeup = Makeup(
        id = makeupDB.size(),
        professor = prof,
        title = title,
        eval_date = datetime.strptime(eval_date, "%Y-%m-%d")
    )
    res = makeupDB.create(new_makeup)
    response = templates.TemplateResponse("prof.html", {"request": request, "user":prof, "prof_makeups":get_prof_makeups(prof)})
    return response

@app.get('/makeup/{makeup_id}/close', response_class=HTMLResponse)
async def close_makeup(request:Request, makeup_id:int, prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    res = makeupDB.close_makeup(makeup_id)
    response = templates.TemplateResponse("prof.html", {"request": request, "user":prof, "prof_makeups":get_prof_makeups(prof)})
    return response

@app.get('/makeup/prof', response_model=List[Makeup])
def get_prof_makeups(prof: UserView = Depends(get_current_prof)):
    return makeupDB.get_prof(prof.username)

@app.get('/makeup/open', response_model=List[Makeup])
def get_open_makeups(stud: UserView = Depends(get_current_stud)):
    return makeupDB.get_open()

################################################ Request Endpoints ###############################################
@app.get('/request', response_model=List[MRequest])
def get_all_requests():
    return requestDB.get_all()

@app.post('/request/{makeup_id}', response_class=HTMLResponse)
async def create_new_request(request:Request, makeup_id:int, block_index:int = Form(...), stud: UserView = Depends(get_current_stud)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup or not original_makeup.isOpen:
        raise HTTPException(status_code=404, detail='Not Found')
    new_request = MRequest(
        id = requestDB.size(),
        student = stud,
        block_index = block_index,
        makeup = makeupDB.read(makeup_id),
    )
    res = requestDB.create(new_request)
    response = templates.TemplateResponse("stud.html", {"request": request, "user":stud, "student_requests":get_stud_requests(stud), "open_makeups":get_open_makeups(stud) })
    return response

@app.get('/request/stud', response_model=List[MRequest])
def get_stud_requests(stud: UserView = Depends(get_current_stud)):
    return requestDB.get_student(stud.username)

@app.get('/request/prof/{makeup_id}', response_class=HTMLResponse)
def get_makeup_requests(request:Request, makeup_id:int, prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    
    makeup_requests = requestDB.get_makeup(makeup_id)
    response = templates.TemplateResponse("requests.html", {"request": request, "user":prof, "makeup":original_makeup, "makeup_requests":makeup_requests})
    return response

############################################# Prescription Endpoints #############################################
# endpoint to submit visitation document
@app.post("/prescription", response_class=HTMLResponse)
def mine_block(
    request:Request,
    img_file:UploadFile = File(...), 
    student_username:str = Form(...), 
    rest_duration:int = Form(...), 
    doc: UserView = Depends(get_current_doc)
):
    if not img_file.filename.endswith(".png"):
        return HTTPException(status_code=400, detail="Invalid File Format")
    
    try:
        img_file.filename = "presc_" + student_username +'_'+ datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ".png"
        print("FILE", img_file.filename)
        contents = img_file.file.read()
        print("CONTENTS", len(contents))
        with open(img_file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return HTTPException(status_code=500, detail="File Upload Failed")
    finally:
        img_file.file.close()
    
    prescription = Prescription(
        student_username = student_username,
        rest_duration = rest_duration,
        scan_img = img_file.filename,
        img_hash = hashlib.sha256(contents).hexdigest(),
    )

    prescription.signature = crypto.sign_message(prescription.get_data_str())

    block = blockchain.mine_block(data=prescription)
    print("BLOCK", block)
    response = templates.TemplateResponse("prescription.html", {"request": request, "user":doc, "block":block})
    return response

####################################### Verification and Approval Endpoints ######################################
# endpoint to verify request document
@app.get("/makeup/{makeup_id}/verify", response_class=RedirectResponse, status_code=303)
async def verify_request_bulk(makeup_id:int, prof: UserView = Depends(get_current_prof)):
    original_makeup = makeupDB.read(makeup_id)
    if not original_makeup:
        raise HTTPException(status_code=404, detail='Not Found')
    if original_makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')

    for req in requestDB.get_makeup(makeup_id):
        block = blockchain.get_block_from_index(req.block_index)
        if not block:
            req.verified = False
            req.verification_comment = "Prescription Not Found"
            requestDB.update(req.id, req)
        
        elif req.student.username != block.data.student_username:
            req.verified = False
            req.verification_comment = "Student Username Did Not Match"
            requestDB.update(req.id, req)

        # Signature Verification
        elif not crypto.verify_signature(block.data.get_data_str(), block.data.signature):
            req.verified = False
            req.verification_comment = "Signature Verification Failed"
            req.verification_output = block.data
            requestDB.update(req.id, req)

        elif req.makeup.eval_date - block.timestamp > timedelta(days=block.data.rest_duration):
            req.verified = False
            req.verification_comment = "Evaluation Date Not In Rest period"
            req.verification_output = block.data
            requestDB.update(req.id, req)

        else:
            req.verified = True
            req.verification_comment = "Student ID matched; Signature Verified; Date checked; Successful"
            req.verification_output = block.data
            requestDB.update(req.id, req)
    
    return '/request/prof/{}'.format(original_makeup.id)

@app.get("/request/{req_id}/verify", response_class=RedirectResponse, status_code=303)
async def verify_request(req_id: int, prof: UserView = Depends(get_current_prof)):
    req: MRequest = requestDB.read(req_id)
    if not req:
        return HTTPException(status_code=404, detail="Not Found")

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
        req.verification_comment = "Student ID matched; Signature Verified; Date checked; Successful"
        req.verification_output = block.data
        requestDB.update(req_id, req)
    
    return '/request/prof/{}'.format(req.makeup.id)


@app.post('/request/{request_id}/approve', response_class=RedirectResponse, status_code=303)
async def approve_request(request_id:int, approval_value: bool = Form(False), approval_comment: str = Form(...), prof: UserView = Depends(get_current_prof)):
    req = requestDB.read(request_id)
    if not req:
        raise HTTPException(status_code=404, detail='Not Found')
    if req.makeup.professor.username != prof.username:
        raise HTTPException(status_code=401, detail='Not Authorized')
    
    req.approved = approval_value
    req.approval_comment = approval_comment
    req = requestDB.update(request_id,req)
    return '/request/prof/{}'.format(req.makeup.id)


@app.get("/image/{request_id}", response_class=FileResponse)
async def show_image(request_id:int, prof: UserView = Depends(get_current_prof)):
    req = requestDB.read(request_id)
    if not req:
        raise HTTPException(status_code=404, detail='Not Found')
    if not req.verification_output:
        raise HTTPException(status_code=401, detail='Not Authorized')
    
    return req.verification_output.scan_img

################################################# Test Endpoints #################################################
# endpoint to return the entire blockchain
@app.get("/test/blockchain/")
def get_blockchain():
    chain = blockchain.chain
    return chain

# endpoint to check if the chain is valid
@app.get("/test/validate/")
def is_blockchain_valid():
    if not blockchain.is_chain_valid():
        return HTTPException(status_code=400, detail="The blockchain is invalid")

    return blockchain.is_chain_valid()
