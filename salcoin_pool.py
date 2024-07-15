from salcoin_transaction import Transaction, TxIn, UnspentTxOut, validateTransaction
from copy import deepcopy
from itertools import chain


transactionPool = []

def getTransactionPool():
    return deepcopy(transactionPool)

def addToTransactionPool(tx, unspentTxOuts):
    global transactionPool
    if not validateTransaction(tx, unspentTxOuts):
        raise Exception('Trying to add invalid tx to pool')
    if not isValidTxForPool(tx, transactionPool):
        raise Exception('Trying to add invalid tx to pool')
    print('adding to txPool:',tx.to_dict())
    transactionPool.append(tx)

def hasTxIn(txIn, unspentTxOuts):
    for uTxO in unspentTxOuts:
        if uTxO.txOutId == txIn.txOutId and uTxO.txOutIndex == txIn.txOutIndex:
            return True
    return False

def updateTransactionPool(unspentTxOuts):
    global transactionPool
    invalidTxs = []
    for tx in transactionPool:
        for txIn in tx.tx_ins:
            if not hasTxIn(txIn, unspentTxOuts):
                invalidTxs.append(tx)
                break
    if len(invalidTxs) > 0:
        print('removing the following transactions from txPool:')
        for tx in invalidTxs:
            print(tx.to_dict())
    transactionPool = [tx for tx in transactionPool if tx not in invalidTxs]


def getTxPoolIns(aTransactionPool):
    return list(chain.from_iterable(tx.tx_ins for tx in aTransactionPool))

def isValidTxForPool(tx, aTransactionPool):
    txPoolIns = getTxPoolIns(aTransactionPool)

    def containsTxIn(txIns, txIn):
        for txPoolIn in txPoolIns:
            if txIn.txOutIndex == txPoolIn.txOutIndex and txIn.txOutId == txPoolIn.txOutId:
                return True
        return False
    
    for txIn in tx.tx_ins:
        if containsTxIn(txPoolIns, txIn):
            print('txIn already found in the txPool')
            return False
    return True