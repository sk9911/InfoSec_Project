import datetime as _dt
import hashlib as _hashlib
import json as _json


class Blockchain:
    def __init__(self):
        self.chain = list()
        initial_block = self._create_block(
            data="genesis block", nonce=1, previous_hash="0", index=1
        )
        self.chain.append(initial_block)

    def mine_block(self, data: str) -> dict:
        previous_block = self._get_previous_block()
        previous_nonce = previous_block["nonce"]
        index = len(self.chain)
        nonce = self._proof_of_work(
            previous_nonce=previous_nonce, index=index, data=data
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            data=data, nonce=nonce, previous_hash=previous_hash, index=index
        )
        self.chain.append(block)
        return block

    def _create_block(
        self, data: str, nonce: int, previous_hash: str, index: int
    ) -> dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
            "data": data,
            "nonce": nonce,
            "previous_hash": previous_hash,
        }

        return block

    def _get_previous_block(self) -> dict:
        return self.chain[-1]
    
    def get_data_from_index(self,index: int) -> dict:
        return self.chain[index]["data"]

    def _to_digest(
        self, new_nonce: int, previous_nonce: int, index: int, data: str
    ) -> bytes:
        to_digest = str(new_nonce ** 2 - previous_nonce ** 2 + index) + data
        # It returns an utf-8 encoded version of the string
        return to_digest.encode()

    def _proof_of_work(self, previous_nonce: str, index: int, data: str) -> int:
        new_nonce = 1
        check_nonce = False

        while not check_nonce:
            to_digest = self._to_digest(new_nonce, previous_nonce, index, data)
            hash_operation = _hashlib.sha256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_nonce = True
            else:
                new_nonce += 1

        return new_nonce

    def _hash(self, block: dict) -> str:
        """
        Hash a block and return the crytographic hash of the block
        """
        encoded_block = _json.dumps(block, sort_keys=True).encode()

        return _hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            # Check if the previous hash of the current block is the same as the hash of it's previous block
            if block["previous_hash"] != self._hash(previous_block):
                return False

            previous_nonce = previous_block["nonce"]
            index, data, nonce = block["index"], block["data"], block["nonce"]
            hash_operation = _hashlib.sha256(
                self._to_digest(
                    new_nonce=nonce,
                    previous_nonce=previous_nonce,
                    index=index,
                    data=data,
                )
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1

        return True
