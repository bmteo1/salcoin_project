import hashlib
from ecdsa import SigningKey, SECP256k1
from collections import Counter
from Crypto.Hash import RIPEMD160

COINBASE_AMOUNT = 50

class UnspentTxOut: 
    def __init__(self, txOutId, txOutIndex, address, amount):
        self.txOutId = txOutId
        self.txOutIndex = txOutIndex
        self.address = address
        self.amount = amount
    
class TxOut:
    def __init__(self, address: str, amount: int):
        self.address = address
        self.amount = amount

class Transaction:
    def __init__(self, id: str, tx_ins: list, tx_outs: list):
        self.id = id
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs

class TxIn:
    def __init__(self, txOutId: str, txOutIndex: int, signature: str):
        self.txOutId = txOutId
        self.txOutIndex = txOutIndex
        self.signature = signature

def getTransactionId(transaction: Transaction) -> str:
    txInContent = ''.join([txIn.txOutId + str(txIn.txOutIndex) for txIn in transaction.tx_ins])
    txOutContent = ''.join([txOut.address + str(txOut.amount) for txOut in transaction.tx_outs])
    return RIPEMD160.new().update(hashlib.sha256((txInContent + txOutContent).encode('utf-8')).digest()).hexdigest()


def validateTransaction(transaction: Transaction, unspentTxOuts):
    if not isValidTransactionStructure(transaction):
        return False
    if getTransactionId(transaction) != transaction.id:
        print('invalid tx id: ' + transaction.id)
        return False

    hasValidTxIns = map(lambda txIn: validateTxIn(txIn, transaction, unspentTxOuts), transaction.tx_ins)
    if not reduce(lambda a, b: a and b, hasValidTxIns, True):
        print('some of the txIns are invalid in tx: ' + transaction.id)
        return False
    totalTxInValues = map(lambda txIn: getTxInAmount(txIn, unspentTxOuts), transaction.tx_ins)
    if sum(totalTxInValues) != sum(map(lambda txOut: txOut.amount, transaction.tx_outs)):
        print('totalTxOutValues !== totalTxInValues in tx: ' + transaction.id)
        return False
    return True


def validateBlockTransactions(transactions, unspentTxOuts, blockIndex):
    coinbaseTx = transactions[0]
    if not validateCoinbaseTx(coinbaseTx, blockIndex):
        print('invalid coinbase transaction: ' + str(coinbaseTx))
        return False

    txIns = [tx.txIns for tx in transactions]
    if hasDuplicates(txIns):
        return False

    normalTransactions = transactions[1:]
    validations = [validate_transaction(tx, unspent_tx_outs) for tx in normal_transactions]
    return all(validations)

def hasDuplicates(tx_ins):
    groups = Counter([tx_in.tx_out_id + str(tx_in.tx_out_index) for tx_in in tx_ins])
    for key, value in groups.items():
        if value > 1:
            print(f'duplicate txIn: {key}')
            return True
    
    return False

def validateCoinbaseTx(transaction, blockIndex):
    if transaction is None:
        print('The first transaction in the block must be coinbase transaction')
        return False
    
    if getTransactionId(transaction) != transaction.id:
        print('invalid coinbase tx id: ' + transaction.id)
        return False
    
    if len(transaction.tx_ins) != 1:
        print('one txIn must be specified in the coinbase transaction')
        return False
    
    if transaction.tx_ins[0].tx_out_index != blockIndex:
        print('the txIn signature in coinbase tx must be the block height')
        return False
    
    if len(transaction.tx_outs) != 1:
        print('invalid number of txOuts in coinbase transaction')
        return False
    
    if transaction.tx_outs[0].amount != COINBASE_AMOUNT:
        print('invalid coinbase amount in coinbase transaction')
        return False
    
    return True

def find_utxo(a_unspent_tx_outs):
    for utxo in a_unspent_tx_outs:
        if utxo.tx_out_id == tx_in.tx_out_id and utxo.tx_out_index == tx_in.tx_out_index:
            return utxo

def validateTxIn(txIn, transaction, unspentTxOuts):
    referencedUTxOut = find_utxo(unspentTxOuts)
    if referencedUTxOut is None:
        print('referenced txOut not found: ' + json.dumps(txIn))
        return False
        
    address = referencedUTxOut.address
    key = SigningKey.from_string(bytes.fromhex(address), curve=SECP256k1)
    validSignature = key.verify(bytes.fromhex(txIn.signature), transaction.id.encode('utf-8'))
    if not validSignature:
        print('invalid txIn signature: %s txId: %s address: %s', txIn.signature, transaction.id, referencedUTxOut.address)
        return False
    return True

def getTxInAmount(tx_in, a_unspent_tx_outs):
    referenced_utxo = findUnspentTxOut(tx_in.txOutId, tx_in.txOutIndex, a_unspent_tx_outs)
    if referenced_utxo:
        return referenced_utxo.amount
    else:
        raise ValueError('Could not find referenced txOut')

def findUnspentTxOut(transactionId, index, aUnspentTxOuts):
    for utxo in aUnspentTxOuts:
        if utxo.txOutId == transactionId and utxo.txOutIndex == index:
            return utxo
    return None

def getCoinbaseTransaction(address, blockIndex):
    txIn = TxIn()
    txIn.signature = ''
    txIn.txOutId = ''
    txIn.txOutIndex = blockIndex

    t = Transaction()
    t.tx_ins = [txIn]
    t.tx_outs = [TxOut(address, COINBASE_AMOUNT)]
    t.id = getTransactionId(t)
    return t


def signTxIn(transaction, txInIndex, privateKey, aUnspentTxOuts):
    txIn = transaction.tx_ins[txInIndex]
    dataToSign = transaction.id
    referencedUnspentTxOut = findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, aUnspentTxOuts)
    if referencedUnspentTxOut is None:
        print('could not find referenced txOut')
        raise ValueError('could not find referenced txOut')
    
    referencedAddress = referencedUnspentTxOut.address
    if getPublicKey(privateKey) != referencedAddress:
        print('trying to sign an input with private key that does not match the address that is referenced in txIn')
        raise ValueError('trying to sign an input with private key that does not match the address that is referenced in txIn')
    
    key = SigningKey.from_string(bytes.fromhex(privateKey), curve=SECP256k1)
    signature = key.sign(dataToSign.encode('utf-8')).to_string()
    return signature

def updateUnspentTxOuts(transactions, unspentTxOuts):
    newUnspentTxOuts = [
        UnspentTxOut(t.id, index, tx_out.address, tx_out.amount)
        for t in transactions
        for index, tx_out in enumerate(t.tx_outs)
    ]

    consumedTxOuts = [
        UnspentTxOut(tx_in.tx_out_id, tx_in.tx_out_index, '', 0.0)
        for t in transactions
        for tx_in in t.tx_ins
    ]

    resultingUnspentTxOuts = [
        u_tx_o
        for u_tx_o in unspentTxOuts
        if not any(u_tx_o.txOutId == tx_out.txOutId and u_tx_o.txOutIndex == tx_out.txOutIndex for tx_out in consumedTxOuts)
    ] + newUnspentTxOuts

    return resultingUnspentTxOuts

def processTransactions(aTransactions, aUnspentTxOuts, blockIndex):
    if not validateBlockTransactions(aTransactions, aUnspentTxOuts, blockIndex):
        print('invalid block transactions')
        return None
    return updateUnspentTxOuts(aTransactions, aUnspentTxOuts)


def toHexString(byteArray):
    return ''.join([f'{byte & 0xFF:02x}' for byte in byteArray])

def getPublicKey(privateKey):
    return SigningKey.from_string(bytes.fromhex(privateKey), curve=SECP256k1).verifying_key.to_string().hex()


def isValidTxInStructure(txIn):
    if txIn is None:
        print('txIn is null')
        return False
    elif not isinstance(txIn.signature, str):
        print('invalid signature type in txIn')
        return False
    elif not isinstance(txIn.txOutId, str):
        print('invalid txOutId type in txIn')
        return False
    elif not isinstance(txIn.txOutIndex, int):
        print('invalid txOutIndex type in txIn')
        return False
    else:
        return True

def isValidTxOutStructure(txOut):
    if txOut is None:
        print('txOut is null')
        return False
    elif not isinstance(txOut.address, str):
        print('invalid address type in txOut')
        return False
    elif not isValidAddress(txOut.address):
        print('invalid TxOut address')
        return False
    elif not isinstance(txOut.amount, int):
        print('invalid amount type in txOut')
        return False
    else:
        return True

def isValidTransactionStructure(transaction):
    if not isinstance(transaction.id, str):
        print('transaction id is not a string')
        return False
    elif not isinstance(transaction.tx_ins, list):
        print('transaction txIns are not an array')
        return False
    elif not isinstance(transaction.tx_outs, list):
        print('transaction txOuts are not an array')
        return False
    elif not all(map(isValidTxOutStructure, transaction.tx_outs)):
        print('invalid txOut structure in transaction')
        return False
    elif not all(map(isValidTxInStructure, transaction.tx_ins)):
        print('invalid txIn structure in transaction')
        return False
    else:
        return True

def isValidAddress(address):
    if len(address) != 130:
        print(address)
        print('invalid public key length')
        return False
    elif re.match('^[a-fA-F0-9]+$', address) is None:
        print('public key must contain only hex characters')
        return False
    elif not address.startswith('04'):
        print('public key must start with 04')
        return False
    return True

