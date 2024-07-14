import json
import os
from pathlib import Path
import hashlib
import random
from ecdsa import SigningKey, SECP256k1
from salcoin_transaction import getPublicKey, getTransactionId, signTxIn, Transaction, TxIn, TxOut, UnspentTxOut
from Crypto.Hash import RIPEMD160


sk = SigningKey.generate(curve=SECP256k1)
privateKeyLocation = os.getenv('PRIVATE_KEY', 'secret/private')

def getPrivateFromWallet():
    privateKeyLocation = os.getenv('PRIVATE_KEY',  'secret/private')
    with open(privateKeyLocation, 'r') as file:
        privateKey = file.read().strip()
    return privateKey

def getPublicFromWallet():
    privateKey = getPrivateFromWallet()
    privateKey = SigningKey.from_string(bytes.fromhex(privateKey), curve=SECP256k1)
    publicKey = privateKey.get_verifying_key().to_string().hex()
    return '0310'+publicKey

def generatePrivateKey():
    sk = SigningKey.generate(curve=SECP256k1)
    privateKey = sk.to_string().hex()
    return privateKey

def initWallet():
    if os.path.exists(privateKeyLocation):
        return
    newPrivateKey = generatePrivateKey()
    with open(privateKeyLocation, 'w') as file:
        file.write(newPrivateKey)
    print(f'New wallet with private key created at: {privateKeyLocation}')

def deleteWallet():
    if os.path.exists(privateKeyLocation):
        os.remove(privateKeyLocation)

def getBalance(address, unspentTxOuts):
    return sum([uTxO.amount for uTxO in findUnspentTxOuts(address, unspentTxOuts)])

def findUnspentTxOuts(ownerAddress, unspentTxOuts):
    if unspentTxOuts is None:
        return []
    return [uTxO for uTxO in unspentTxOuts if uTxO.address == ownerAddress]

def findTxOutsForAmount(amount, myUnspentTxOuts):
    currentAmount = 0
    includedUnspentTxOuts = []
    for myUnspentTxOut in myUnspentTxOuts:
        includedUnspentTxOuts.append(myUnspentTxOut)
        currentAmount += myUnspentTxOut.amount
        if currentAmount >= amount:
            leftOverAmount = currentAmount - amount
            return (includedUnspentTxOuts, leftOverAmount)

    eMsg = f'Cannot create transaction from the available unspent transaction outputs. Required amount: {amount}. Available unspentTxOuts: {json.dumps([i.to_dict() for i in myUnspentTxOuts])}'
    raise ValueError(eMsg)

def createTxOuts(receiverAddress, myAddress, amount, leftOverAmount):
    txOut1 = TxOut(receiverAddress, amount)
    if leftOverAmount == 0:
        return [txOut1]
    else:
        leftOverTx = TxOut(myAddress, leftOverAmount)
        return [txOut1, leftOverTx]

def filterTxPoolTxs(unspentTxOuts, transactionPool):
    txIns = [tx.tx_ins for tx in transactionPool]
    removable = []
    for unspentTxOut in unspentTxOuts:
        txIn = next((aTxIn for aTxIn in txIns if aTxIn.txOutIndex == unspentTxOut.txOutIndex and aTxIn.txOutId == unspentTxOut.txOutId), None)
        if txIn is None:
            pass
        else:
            removable.append(unspentTxOut)

    return [uTxO for uTxO in unspentTxOuts if uTxO not in removable]

def createTransaction(receiverAddress, amount, privateKey,unspentTxOuts, txPool):
    myAddress = getPublicFromWallet()
    myUnspentTxOutsA = [uTxO for uTxO in unspentTxOuts if uTxO.address == myAddress]
    myUnspentTxOuts = filterTxPoolTxs(myUnspentTxOutsA, txPool)    
    includedUnspentTxOuts, leftOverAmount = findTxOutsForAmount(amount, myUnspentTxOuts)
    unsignedTxIns = [TxIn(txOut.txOutId, txOut.txOutIndex,'') for txOut in includedUnspentTxOuts]
    tx = Transaction(tx_ins=unsignedTxIns, tx_outs=createTxOuts(receiverAddress, myAddress, amount, leftOverAmount))
    tx.id = getTransactionId(tx)
    for index, txIn in enumerate(tx.tx_ins):
        tx.tx_ins[index].signature = signTxIn(tx, index, privateKey, unspentTxOuts)
    return tx

def signTxIn(transaction, txInIndex, privateKey, unspentTxOuts):
    txIn = transaction.tx_ins[txInIndex]
    dataToSign = transaction.id
    referencedUnspentTxOut = findUnspentTxOutByTxIn(txIn, unspentTxOuts)

    if referencedUnspentTxOut is None:
        raise ValueError(f'Referenced txOut not found: {json.dumps(txIn.to_dict())}')

    privateKey = SigningKey.from_string(bytes.fromhex(privateKey), curve=SECP256k1)
    signature = privateKey.sign(dataToSign.encode())
    return signature.hex()

def findUnspentTxOutByTxIn(txIn, unspentTxOuts):
    return next((uTxO for uTxO in unspentTxOuts if uTxO.txOutId == txIn.txOutId and uTxO.txOutIndex == txIn.txOutIndex), None)