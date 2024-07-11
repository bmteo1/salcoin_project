import hashlib
import time
from Crypto.Hash import RIPEMD160
from copy import deepcopy
import math
from salcoin_communication import broadcastLatest, broadcastTransactionPool
from salcoin_transaction import getCoinbaseTransaction, isValidAddress, processTransactions, Transaction, UnspentTxOut, TxIn, TxOut
from salcoin_pool import addToTransactionPool, getTransactionPool, updateTransactionPool
from salcoin_wallets import createTransaction, findUnspentTxOuts, getBalance, getPrivateFromWallet, getPublicFromWallet

class Block:
    def __init__(self,index, previous_hash,
                timestamp, data, difficulty, minterBalance, minterAddress):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.minterBalance = minterBalance
        self.minterAddress = minterAddress
        self.current_hash = self.hash_block()
    
    def hash_block(self):
        sha256 = hashlib.sha256()
        sha256.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)+ str(self.minterAddress)+str(self.minterBalance)+str(self.difficulty)).encode('utf-8'))
        sha256_hash = sha256.digest()
        ripemd160 = RIPEMD160.new()
        ripemd160.update(sha256_hash)
        return ripemd160.hexdigest()

# genesisTransaction = {
#     'tx_ins': [{'signature': '', 'txOutId': '', 'txOutIndex': 0}],
#     'tx_outs': [{
#         'address': '04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a',
#         'amount': 50
#     }],
#     'id': 'e655f6a5f26dc9b4cac6e46f52336428287759cf81ef5ff10854f69d68f43fa3'
# }
genesisTransaction = Transaction(
    id =  '75205d1fe27602cddb09ca12487051ce20719a7a',
    tx_ins = [TxIn(signature="", txOutId='', txOutIndex=0)],
    tx_outs = [TxOut(address='04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a', amount=50)]
)

genesisBlock = Block(
    0, '91a73664bc84c0baa1fc75ea6e4aa6d1d20c5df664c724e3159aefc2e1186627', int(time.time()), [genesisTransaction], 0, 0, "04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a"
)

mintingWithoutCoinIndex = 100
blockchain = [genesisBlock]
unspentTxOuts = processTransactions(blockchain[0].data, [], 0)

def getBlockchain():
    return blockchain

def getUnspentTxOuts():
    return  deepcopy(unspentTxOuts)

def setUnspentTxOuts(newUnspentTxOut):
    unspentTxOuts = newUnspentTxOut

def getLatestBlock():
    return blockchain[-1]

LOCK_GENERATION_INTERVAL= 10
DIFFICULTY_ADJUSTMENT_INTERVAL = 10

def getAdjustedDifficulty(latestBlock, aBlockchain):
    prevAdjustmentBlock = aBlockchain[blockchain.length - DIFFICULTY_ADJUSTMENT_INTERVAL]
    timeExpected = BLOCK_GENERATION_INTERVAL * DIFFICULTY_ADJUSTMENT_INTERVAL
    timeTaken = latestBlock.timestamp - prevAdjustmentBlock.timestamp
    if timeTaken < timeExpected / 2:
        return prevAdjustmentBlock.difficulty + 1
    elif timeTaken > timeExpected * 2:
        return prevAdjustmentBlock.difficulty - 1
    else:
        return prevAdjustmentBlock.difficulty

def getDifficulty(aBlockchain):
    latestBlock = aBlockchain[-1]
    if latestBlock.index % DIFFICULTY_ADJUSTMENT_INTERVAL == 0 and latestBlock.index != 0:
        return getAdjustedDifficulty(latestBlock, aBlockchain)
    else:
        return latestBlock.difficulty

def getCurrentTimestamp():
     return int(time.time())

def generateRawNextBlock(blockData):
    previousBlock = getLatestBlock()
    difficulty = getDifficulty(getBlockchain())
    nextIndex = previousBlock.index + 1
    newBlock = findBlock(nextIndex, previousBlock.current_hash, blockData, difficulty)
    if addBlockToChain(newBlock):
        broadcastLatest()
        return newBlock
    else:
        return None

def getMyUnspentTransactionOutputs():
    return findUnspentTxOuts(getPublicFromWallet(), getUnspentTxOuts())

def generateNextBlock():
    coinbaseTx = getCoinbaseTransaction(getPublicFromWallet(), getLatestBlock().index + 1)
    blockData = [coinbaseTx].concat(getTransactionPool())
    return generateRawNextBlock(blockData)

def generatenextBlockWithTransaction(receiverAddress, amount):
    if not isValidAddress(receiverAddress):
        raise Exception('invalid address')
    if not isinstance(amount, int):
        raise Exception('invalid amount')
    coinbaseTx = getCoinbaseTransaction(getPublicFromWallet(), getLatestBlock().index + 1)
    tx = createTransaction(receiverAddress, amount, getPrivateFromWallet(), getUnspentTxOuts(), getTransactionPool())
    blockData = [coinbaseTx, tx]
    return generateRawNextBlock(blockData)

def findBlock(index, previousHash, data, difficulty):
    pastTime = 0
    while True:
        timestamp = int(time.time())
        if pastTime != timestamp:
            if isBlockStakingValid(previousHash, getPublicFromWallet(), timestamp, getAccountBalance(), difficulty, index):
                return Block(index, previousHash, data, timestamp, difficulty, getAccountBalance(), getPublicFromWallet())
            pastTime = timestamp

def getAccountBalance():
    return getBalance(getPublicFromWallet(), getUnspentTxOuts())

def sendTransaction(address, amount):
    tx = createTransaction(address, amount, getPrivateFromWallet(), getUnspentTxOuts(), getTransactionPool())
    addToTransactionPool(tx, getUnspentTxOuts())
    broadCastTransactionPool()
    return tx

def getAccumulatedDifficulty(aBlockchain):
    return sum([math.pow(2, block['difficulty']) for block in ablockchain])

def isValidBlockStructure(block):
    return isinstance(block.index, int) and isinstance(block.previous_hash, str) and isinstance(block.data, str) and isinstance(block.current_hash, str) and isinstance(block.difficulty, int) and isinstance(block.minterBalance, int) and isinstance(block.minterAddress, str)

def isValidNewBlock(newBlock, previousBlock):
    if previousBlock.index + 1 != newBlock.index:
        print('invalid index')
        return False
    elif previousBlock.current_hash != newBlock.previous_hash:
        print('invalid previoushash')
        return False
    elif not isValidTimestamp(newBlock, previousBlock):
        print('invalid timestamp')
        return False
    elif not hasValidHash(newBlock):
        return False
    return True

def isValidTimestamp(newBlock, previousBlock):
    return ( previousBlock.timestamp - 60 < newBlock.timestamp ) and newBlock.timestamp - 60 < getCurrentTimestamp()

def hasValidHash(block):
    if not hashMatchesBlockContent(block):
        print('invalid hash, got:' + block.current_hash)
        return False
    if not isBlockStakingValid(block.previous_hash, block.timestamp, block.minterBalance, block.difficulty, block.index):
        print('staking hash not lower than balance over diffculty times 2^256')
    return True

def calculateHashForBlock(block):
    sha256 = hashlib.sha256()
    sha256.update((str(block.index) + str(block.timestamp) + str(block.data) + str(block.previousHash)+ str(block.minterAddress)+str(block.minterBalance)+str(block.difficulty)).encode('utf-8'))
    sha256_hash = sha256.digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_hash)
    return ripemd160.hexdigest()

def hashMatchesBlockContent(block):
    blockHash = calculateHashForBlock(block)
    return blockHash == block.current_hash

def isBlockStakingValid(prevhash, timestamp, balance, difficulty, index):
    difficulty = int(difficulty) + 1
    if int(index) <= mintingWithoutCoinIndex:
        balance = int(balance) + 1
    
    balanceOverDifficulty = (Decimal(2) ** 256) * Decimal(balance) / Decimal(difficulty)
    stakingHash_temp = RIPEMD160.new().update(hashlib.sha256().update((str(timestamp) + str(prevhash)+ str(address)).encode('utf-8')).digest()).hexdigest()
    decimalStakingHash = Decimal(int(stakingHash_temp, 16))

    difference = balanceOverDifficulty - decimalStakingHash
    return difference >= 0

def isValidChain(blockchainToValidate):
    print('isValidChain:')
    print(json.dumps(blockchainToValidate))

    def isValidGenesis(block):
        return json.dumps(block) == json.dumps(genesisBlock)

    if not isValidGenesis(blockchainToValidate[0]):
        return None

    aUnspentTxOuts = []
    for i in range(0, len(blockchainToValidate)):
        currentBlock = blockchainToValidate[i]
        if i != 0 and not isValidNewBlock(blockchainToValidate[i], blockchainToValidate[i - 1]):
            return None
        aUnspentTxOuts = processTransactions(currentBlock.data, aUnspentTxOuts, currentBlock.index)
        if aUnspentTxOuts == None:
            print('invalid transactions in blockchain')
            return None
    return aUnspentTxOuts 

def addBlockToChain(newBlock):
    if isValidNewBlock(newBlock, getLatestBlock()):
        retVal = processTransactions(newBlock.data, getUnspentTxOuts(), newBlock.index)
        if retVal == None:
            print('block is not valid in terms of transactions')
            return False
        else:
            blockchain.append(newBlock)
            setUnspentTxOuts(retVal)
            updateTransactionPool(unspentTxOuts)
            return True
    return False

def replaceChain(newBlocks):
    aUnspentTxOuts = isValidChain(newBlocks)
    validChain = aUnspentTxOuts != None
    if validChain and getAccumulatedDifficulty(newBlocks) > getAccumulatedDifficulty(getBlockchain()):
        print('Received blockchain is valid. Replacing current blockchain with received blockchain')
        blockchain = newBlocks
        setUnspentTxOuts(aUnspentTxOuts)
        updateTransactionPool(unspentTxOuts)
        broadcastLatest()
    else:
        print('Received blockchain invalid')

def handleReceivedTransaction(transaction):
    addToTransactionPool(transaction, getUnspentTxOuts())