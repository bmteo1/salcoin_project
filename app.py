from flask import Flask, request, jsonify
from salcoin_block import *
from salcoin_communication import connectToPeers, getSockets, initP2PServer
from salcoin_transaction import UnspentTxOut
from salcoin_pool import getTransactionPool
from salcoin_wallets import getPublicFromWallet, initWallet

app = Flask(__name__)

server_port = 3001
peer_port = 5000

initHttpServer(server_port)
initP2PServer(peer_port)
initWallet()

@app.route('/blocks', methods=['GET'])
def blocks():
    return jsonify(getBlockchain())

@app.route('/block/<int:hash>', methods=['GET'])
def get_block(hash):
    blockchain = getBlockchain()
    block = next((b for b in blockchain if b['hash'] == hash), None)
    if block:
        return jsonify(block), 200
    else:
        return jsonify({'message': 'Block not found'}), 404

@app.route('/transaction/<id>', methods=['GET'])
def get_transaction(id):
    blockchain = getBlockchain()
    tx = next((tx['data'] for b in blockchain for tx in b['data'] if tx['id'] == id), None)
    if tx:
        return jsonify(tx), 200
    else:
        return jsonify({'message': 'Transaction not found'}), 404

@app.route('/address/<address>', methods=['GET'])
def get_unspent_tx_outs(address):
    unspent_tx_outs = getUnspentTxOuts()
    filtered_tx_outs = [uTxO for uTxO in unspent_tx_outs if uTxO['address'] == address]
    return jsonify({'unspentTxOuts': filtered_tx_outs}), 200

@app.route('/unspentTransactionOutputs', methods=['GET'])
def get_unspent_transaction_outputs():
    unspent_tx_outs = getUnspentTxOuts()
    return jsonify(unspent_tx_outs), 200


@app.route('/myUnspentTransactionOutputs', methods=['GET'])
def get_my_unspent_transaction_outputs():
    my_unspent_tx_outs = getMyUnspentTransactionOutputs()
    return jsonify(my_unspent_tx_outs), 200

@app.route('/mintRawBlock', methods=['POST'])
def mint_raw_block():
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({'error': 'data parameter is missing'}), 400
    
    new_block = generateRawNextBlock(data['data'])
    if new_block:
        return jsonify(new_block), 200
    else:
        return jsonify({'error': 'could not generate block'}), 400

@app.route('/mintBlock', methods=['POST'])
def mint_block():
    new_block = generateNextBlock()
    if new_block:
        return jsonify(new_block), 200
    else:
        return jsonify({'error': 'could not generate block'}), 400


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = getAccountBalance()
    return jsonify({'balance': balance}), 200

@app.route('/address', methods=['GET'])
def get_address():
    address = getPublicFromWallet()
    return jsonify({'address': address}), 200

@app.route('/mintTransaction', methods=['POST'])
def mint_transaction():
    data = request.get_json()
    if not data or 'address' not in data or 'amount' not in data:
        return jsonify({'error': 'invalid address or amount'}), 400
    
    address = data['address']
    amount = data['amount']
    try:
        resp = generatenextBlockWithTransaction(address, amount)
        return jsonify(resp), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/sendTransaction', methods=['POST'])
def send_transaction():
    data = request.get_json()
    if not data or 'address' not in data or 'amount' not in data:
        return jsonify({'error': 'invalid address or amount'}), 400
    
    address = data['address']
    amount = data['amount']
    try:
        resp = sendTransaction(address, amount)
        return jsonify(resp), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/transactionPool', methods=['GET'])
def get_transaction_pool():
    transaction_pool = getTransactionPool()
    return jsonify(transaction_pool), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    peers = [f"{s._socket.getpeername()[0]}:{s._socket.getpeername()[1]}" for s in getSockets()]
    return jsonify(peers), 200

@app.route('/addPeer', methods=['POST'])
def add_peer():
    data = request.get_json()
    if not data or 'peer' not in data:
        return jsonify({'error': 'peer parameter is missing'}), 400
    
    peer = data['peer']
    connectToPeers(peer)
    return jsonify({'message': 'Peer added successfully'}), 200

@app.route('/stop', methods=['POST'])
def stop_server():
    exit(0)

if __name__ == '__main__':
    app.run(debug=True, port=3001)