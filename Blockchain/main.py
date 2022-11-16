import fastapi as _fastapi
import blockchain as _blockchain
import json as _json
from datetime import datetime
from datetime import timedelta

blockchain = _blockchain.Blockchain()
app = _fastapi.FastAPI()

# endpoint to submit visitation document
@app.post("/add_visit/")
def mine_block(visit_doc: str):
    if not blockchain.is_chain_valid():
        return _fastapi.HTTPException(status_code=400, detail="The blockchain is invalid")
    
    # visit_doc contains
    ## student_id : string
    ## issue_scale : number #(1,2,3,4,5)
    ## rest_duration : number #(nos of days)
    block = blockchain.mine_block(data=visit_doc)
    return {
        index: block["index"],
        timestamp: block["timestamp"],
        data: block["data"]
    }

# endpoint to verify request document
@app.post("/verify_makeups/")
def verify_visitation(verif_doc: str):
    # verif doc contains
    ## eval_date : datetime.Date
    ## issue_threshold : number #(1,2,3,4,5)
    ## makeup_reqs : [ {
    #### student_id : string
    #### block_index : number
    ## } ]

    doc = _json.load(verif_doc)
    makeup_approved = []
    makeup_rejected = []
    for req in doc['makeup_reqs']:
        block = _json.load(blockchain.get_block_from_index(block_index))
        if block == None:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Block not found"
                })
        elif block['student_id'] != req["student_id"]:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Student ID mismatch"
                })
        elif block[data]['issue_scale'] < verif_doc['issue_threshold']:
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Low scale of Health Issue"
                })
        elif datetime.strptime(verif_doc['eval_date'],"%d-%m-%Y") - datetime.strptime(block['timestamp'],"%d-%m-%Y") > timedelta(days=block['data']['rest_duration']):
            makeup_rejected.append({
                    "student_id": req["student_id"],
                    "block_index":req["block_index"],
                    "error":"Evaluation not in Rest period"
                })
        else:
            makeup_approved.append({"student_id": req["student_id"]})
    
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
