from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketDisconnect
from salcoin_block import *
from salcoin_communication import connectToPeers, getSocket, initP2PServer
from salcoin_transaction import UnspentTxOut, Transaction, getTransactionId
from salcoin_pool import getTransactionPool
from salcoin_wallets import getPublicFromWallet, initWallet
import asyncio
import os
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    address: str
    amount: int

class Peer(BaseModel):
    peer: int

# Start the P2P server
@app.on_event("startup")
async def startup_event():
    await initP2PServer(int(os.getenv('UVICORN_PORT'))+1)
    initWallet()

# Route to get all blocks
@app.get('/blocks', response_model=list[dict])
async def blocks():
    return [i.to_dict() for i in getBlockchain()]

# Route to get a specific block by hash
@app.get('/block/{hash}', response_model=dict)
async def get_block(hash: str):
    blockchain = getBlockchain()
    block = next((b for b in blockchain if b.current_hash == hash), None)
    if block:
        return block.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Block not found")

# Route to get a specific transaction by id
@app.get('/transaction/{id}', response_model=dict)
async def get_transaction(id: str):
    blockchain = getBlockchain()
    tx = next((tx for b in blockchain for tx in b.data if tx.id == id), None)
    if tx:
        return tx.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

# Route to get unspent transaction outputs for an address
@app.get('/address/{address}', response_model=dict)
async def get_unspent_tx_outs(address: str):
    unspent_tx_outs = getUnspentTxOuts()
    filtered_tx_outs = [uTxO.to_dict() for uTxO in unspent_tx_outs if uTxO.address == address]
    if not filtered_tx_outs:
        raise HTTPException(status_code=404, detail="No unspent transactions found")
    return {'unspentTxOuts': filtered_tx_outs}

# Route to get all unspent transaction outputs
@app.get('/unspentTransactionOutputs', response_model=list[dict])
async def get_unspent_transaction_outputs():
    unspent_tx_outs = getUnspentTxOuts()
    if not unspent_tx_outs:
        raise HTTPException(status_code=404, detail="No unspent transactions found")
    return [i.to_dict() for i in unspent_tx_outs]

# Route to get unspent transaction outputs for the current wallet
@app.get('/myUnspentTransactionOutputs', response_model=list[dict])
async def get_my_unspent_transaction_outputs():
    my_unspent_tx_outs = getMyUnspentTransactionOutputs()
    if not my_unspent_tx_outs:
        raise HTTPException(status_code=404, detail="No unspent transactions found")
    return [i.to_dict() for i in my_unspent_tx_outs]

# Route to mint a new block
@app.post('/mintBlock', response_model=dict)
async def mint_block():
    new_block = generateNextBlock()
    if new_block:
        return new_block.to_dict()
    else:
        raise HTTPException(status_code=400, detail="Could not generate block")

# Route to get account balance
@app.get('/balance', response_model=dict)
async def get_balance():
    balance = getAccountBalance()
    return {'balance': balance}

# Route to get public address from wallet
@app.get('/address', response_model=dict)
async def get_address():
    address = getPublicFromWallet()
    return {'address': address}

# Route to mint a transaction
@app.post('/mintTransaction', response_model=dict)
async def mint_transaction(item: Item):
    try:
        resp = generatenextBlockWithTransaction(item.address, item.amount)
        return resp.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route to send a transaction
@app.post('/sendTransaction', response_model=dict)
async def send_transaction(item: Item):
    try:
        resp = sendTransaction(item.address, item.amount)
        return resp.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route to get transaction pool
@app.get('/transactionPool', response_model=list[dict])
async def get_transaction_pool():
    transaction_pool = getTransactionPool()
    return [i.to_dict() for i in transaction_pool]

# Route to get peers
@app.get('/peers', response_model=list[str])
async def get_peers():
    sockets = await getSocket()
    peers = [f"{s.remote_address[0]}:{s.remote_address[1]}" for s in sockets]
    return peers


# Route to add a new peer
@app.post('/addPeer', response_model=dict)
async def add_peer(item:Peer):
    try:
        await connectToPeers(item.peer)
        return {'message': 'Peer added successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route to stop the server
@app.post('/stop', response_model=dict)
def stop_server():
    exit(0)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT')), debug=True)
