import streamlit as st
import hashlib
import json
from time import time
from uuid import uuid4

# ----------------------------
# Blockchain Class
# ----------------------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
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
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Basic Blockchain App", layout="wide")
st.title("🧱 Basic Blockchain (Streamlit Version)")

# Create blockchain instance
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()
    st.session_state.node_identifier = str(uuid4()).replace('-', '')

blockchain = st.session_state.blockchain

# Sidebar options
st.sidebar.header("Blockchain Actions")
choice = st.sidebar.radio("Choose an action:", ["View Blockchain", "Add Transaction", "Mine Block"])

if choice == "View Blockchain":
    st.subheader("Full Blockchain")
    st.json(blockchain.chain)
    st.write(f"🔗 Total Blocks: {len(blockchain.chain)}")

elif choice == "Add Transaction":
    st.subheader("Create a New Transaction")
    sender = st.text_input("Sender")
    recipient = st.text_input("Recipient")
    amount = st.number_input("Amount", min_value=0.0, step=0.1)

    if st.button("Add Transaction"):
        if sender and recipient and amount > 0:
            index = blockchain.new_transaction(sender, recipient, amount)
            st.success(f"✅ Transaction will be added to Block {index}")
        else:
            st.error("⚠️ Please enter all fields correctly.")

elif choice == "Mine Block":
    st.subheader("Mine a New Block")
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    with st.spinner('Mining... this may take a few seconds ⛏'):
        proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender="0", recipient=st.session_state.node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    st.success("🎉 New Block Forged!")
    st.json(block)
