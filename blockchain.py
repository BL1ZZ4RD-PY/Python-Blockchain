import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests
from flask import Flask, jsonify, request

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.node = set()
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.node.add(parsed_url.netloc)
        
    def new_block(self, previous_hash, proof):
        block = {
            "index" : len(self.chain) + 1,
            "timestamp" : time(),
            "transactions" : self.current_transactions,
            'proof' : proof,
            "previous hash" : previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transactions(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount
        })
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if guess_hash[:4] =="0000":
            return True
        return False
    
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f"{last_block}")
            print(f"{block}")
            print("\n-------\n")
            if block["previous hash"] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False
            last_block = block
            current_index += 1
        return True
    
    def resolve_conflict(self):
        neighbors = self.node
        new_chain = None
        max_length = len(self.chain)
        
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        
        return False

app = Flask(__name__)

node_indentifier = str(uuid4()).replace("-", "")

blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transactions(0, node_indentifier, 1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(previous_hash, proof)
    response = {
        "message" : "New Block Forged",
        "index" : block["index"],
        "transactions" : block["transactions"],
        "proof" : block["proof"],
        "previous hash" : block["previous hash"]
    }
    return jsonify(response), 200

@app.route("/transaction/new", methods=["POST"])
def new_transaction():
    values = request.get_json()
    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transactions(values["sender"], values["recipient"], values["amount"])
    response = {"message": f"transaction will be added to the block {index}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain" : blockchain.chain,
        "length" : len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()
    nodes = values.get("nodes")
    if nodes is None:
        return 'Error : please provide a valid list of nodes', 400
    
    for node in nodes:
        blockchain.register_node(node)
        response = {
            'message' : "New node has been added",
            "total nodes" : list(blockchain.node)
        }
        return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflict()
    if replaced:
        response = {
            "message" : "Our chain was replaced",
            "new_chain" : blockchain.chain
        }
    else:
        response = {
            'message' : "Our chain is authorized",
            "chain" : blockchain.chain
        }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)