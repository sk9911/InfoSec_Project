from datetime import date
import hashlib as _hashlib
import json as _json
from Models import Prescription, Block


class Blockchain:
    POW_HASH_PREFIX = "0000"

    def __init__(self):
        self.chain = list()
        self._add_block(data="genesis block", nonce=0, previous_hash="0")

    def _add_block(self, data: Prescription, nonce: int, previous_hash: str) -> Block:
        block = Block(
            index = len(self.chain),
            timestamp = date.today().strftime("%Y-%m-%d"),
            data = data,
            nonce = nonce,
            previous_hash = previous_hash,
        )
        self.chain.append(block)
        return block

    def _get_previous_block(self) -> Block:
        return self.chain[-1]

    def _to_digest(self, new_nonce: int, previous_nonce: int, index: int, content: str) -> bytes:
        to_digest = str(new_nonce ** 2 - previous_nonce ** 2 + index) + content
        # It returns an utf-8 encoded version of the string
        return to_digest.encode()

    def _proof_of_work(self, previous_nonce: int, index: int, data: Prescription) -> int:
        new_nonce = 1
        check_nonce = False
        while not check_nonce:
            digest = self._to_digest(new_nonce, previous_nonce, index, str(data))
            hashed_value = _hashlib.sha256(digest).hexdigest()
            if hashed_value.startswith(self.POW_HASH_PREFIX):
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce

    def _hash(self, block: Block) -> str:
        encoded_block = _json.dumps(block.to_dict(), sort_keys=True).encode()
        return _hashlib.sha256(encoded_block).hexdigest()

    def mine_block(self, data: Prescription) -> Block:
        previous_block = self._get_previous_block()
        previous_nonce = previous_block.nonce
        nonce = self._proof_of_work(previous_nonce=previous_nonce, index=len(self.chain), data=data)
        previous_hash = self._hash(block=previous_block)
        block = self._add_block(data=data, nonce=nonce, previous_hash=previous_hash)
        return block

    def get_block_from_index(self, index: int) -> Block:
        if index > len(self.chain)-1:
            return None
        else:
            return self.chain[index]
    
    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block.previous_hash != self._hash(previous_block):
                return False

            hashed_value = _hashlib.sha256(
                self._to_digest(
                    new_nonce = block.nonce,
                    previous_nonce = previous_block.nonceprevious_nonce,
                    index = block.index,
                    data = block.data,
                )
            ).hexdigest()

            if not hashed_value.startswith(self.POW_HASH_PREFIX):
                return False

            previous_block = block
            block_index += 1

        return True
