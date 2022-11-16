import fastapi as _fastapi
import blockchain as _blockchain
import json as _json

blockchain = _blockchain.Blockchain()
app = _fastapi.FastAPI()

# endpoint to submit visitation document
@app.post("/add_visit/")
def mine_block(data: str):
    if not blockchain.is_chain_valid():
        return _fastapi.HTTPException(status_code=400, detail="The blockchain is invalid")
    block = blockchain.mine_block(data=data)

    return {index: block["index"], data: block["data"], timestamp: block["timestamp"]}

# endpoint to verify request document
@app.post("/verify_makeups/")
def verify_visitation(verification_req_doc: str):
    makeup_approved = []
    makeup_rejected = []
    for student in verification_req_doc['list_of_students']:
        document = _json.load(blockchain.get_data_from_index(index))
        if document == None:
            makeup_rejected.append("Student with ID {} is not present in the visitation document".format(student[1]))
        elif document['student_id'] != student[1]:
            makeup_rejected.append("Student with ID {} is not matched with the entry in the visitation document".format(student[1]))
        elif document['Scale_of_Health'] < verification_req_doc['threshold_lvl']:
            makeup_rejected.append("Student with ID {} is not approved the makeup bcoz of scale_of_health".format(student[1]))
        elif (verification_req_doc['date_of_Eval'] - document['Date_of_Visitation']).days > document['Duration_of_Rest_in_days']:
            makeup_rejected.append("Student with ID {} is not approved the makeup bcoz of date".format(student[1]))
        else:
            makeup_approved.append(student[1])
    return {approved:makeup_approved, rejected:makeup_rejected}

# endpoint to return the entire blockchain
@app.get("/test/blockchain/")
def get_blockchain():
    if not blockchain.is_chain_valid():
        return _fastapi.HTTPException(status_code=400, detail="The blockchain is invalid")
    chain = blockchain.chain
    return chain

# endpoint to check if the chain is valid
@app.get("/test/validate/")
def is_blockchain_valid():
    if not blockchain.is_chain_valid():
        return _fastapi.HTTPException(status_code=400, detail="The blockchain is invalid")

    return blockchain.is_chain_valid()
