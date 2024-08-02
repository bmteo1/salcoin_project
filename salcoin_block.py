import hashlib
import time
from Crypto.Hash import RIPEMD160
from copy import deepcopy
import math
import asyncio
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
        sha256.update((str(self.index) + str(self.timestamp) + str([tx.to_dict() for tx in self.data]) + str(self.previous_hash)+ str(self.minterAddress)+str(self.minterBalance)+str(self.difficulty)).encode('utf-8'))
        sha256_hash = sha256.digest()
        ripemd160 = RIPEMD160.new()
        ripemd160.update(sha256_hash)
        return ripemd160.hexdigest()
    
    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': [tx.to_dict() for tx in self.data],
            'difficulty': self.difficulty,
            'minterBalance': self.minterBalance,
            'minterAddress': self.minterAddress,
            'current_hash': self.current_hash
        }

genesisTransaction = Transaction(
    id =  '6e3b69a20fcbe95a662b991e1cd30869dc045260',
    tx_ins = [TxIn(signature="", txOutId='', txOutIndex=0)],
    tx_outs = [TxOut(address='0310bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a', amount=50)]
)

genesisBlock = Block(
    0, '91a73664bc84c0baa1fc75ea6e4aa6d1d20c5df664c724e3159aefc2e1186627', int(time.time()), [genesisTransaction], 0, 0, "0310bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a"
)

mintingWithoutCoinIndex = 100
blockchain = [genesisBlock]
unspentTxOuts = processTransactions(blockchain[0].data, [], 0)

def getBlockchain():
    return blockchain

def getUnspentTxOuts():
    return deepcopy(unspentTxOuts)

def setUnspentTxOuts(newUnspentTxOut):
    global unspentTxOuts
    unspentTxOuts = newUnspentTxOut

def getLatestBlock():
    return blockchain[-1]

BLOCK_GENERATION_INTERVAL= 10
DIFFICULTY_ADJUSTMENT_INTERVAL = 10

def getAdjustedDifficulty(latestBlock, aBlockchain):
    prevAdjustmentBlock = aBlockchain[len(blockchain) - DIFFICULTY_ADJUSTMENT_INTERVAL]
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

async def generateRawNextBlock(blockData):
    previousBlock = getLatestBlock()
    difficulty = getDifficulty(getBlockchain())
    nextIndex = previousBlock.index + 1
    newBlock = findBlock(nextIndex, previousBlock.current_hash, blockData, difficulty)

    if addBlockToChain(newBlock):
        await broadcastLatest()
        return newBlock
    else:
        return None

def getMyUnspentTransactionOutputs():
    return findUnspentTxOuts(getPublicFromWallet(), getUnspentTxOuts())

async def generateNextBlock():
    coinbaseTx = getCoinbaseTransaction(getPublicFromWallet(), getLatestBlock().index + 1)
    blockData = []
    blockData.append(coinbaseTx)
    for tx in getTransactionPool():
        blockData.append(tx)
    newBlock = await generateRawNextBlock(blockData)
    return newBlock

async def generatenextBlockWithTransaction(receiverAddress, amount):
    if not isValidAddress(receiverAddress):
        raise Exception('invalid address')
    if not isinstance(amount, int):
        raise Exception('invalid amount')
    coinbaseTx = getCoinbaseTransaction(getPublicFromWallet(), getLatestBlock().index + 1)
    tx = createTransaction(receiverAddress, amount, getPrivateFromWallet(), getUnspentTxOuts(), getTransactionPool())
    blockData = [coinbaseTx, tx]
    newBlock = await generateRawNextBlock(blockData)
    return newBlock

def findBlock(index, previous_hash, data, difficulty):
    pastTime = 0
    while True:
        timestamp = int(time.time())
        if pastTime != timestamp:
            if isBlockStakingValid(previous_hash, timestamp, getAccountBalance(), difficulty, index):
                return Block(index, previous_hash, timestamp, data, difficulty, getAccountBalance(), getPublicFromWallet())
            pastTime = timestamp

def getAccountBalance():
    return getBalance(getPublicFromWallet(), getUnspentTxOuts())

async def sendTransaction(address, amount):
    tx = createTransaction(address, amount, getPrivateFromWallet(), getUnspentTxOuts(), getTransactionPool())
    addToTransactionPool(tx, getUnspentTxOuts())
    await broadcastTransactionPool()
    return tx

def getAccumulatedDifficulty(ablockchain):
    return sum([math.pow(2, block.difficulty) for block in ablockchain])

def isValidBlockStructure(block):
    return isinstance(block.index, int) and isinstance(block.previous_hash, str) and isinstance(block.data, list) and isinstance(block.data[0], Transaction) and isinstance(block.current_hash, str) and isinstance(block.difficulty, int) and isinstance(block.minterBalance, int) and isinstance(block.minterAddress, str)

def isValidNewBlock(newBlock, previousBlock):
    if previousBlock.index + 1 != newBlock.index:
        print('invalid index')
        return False
    elif previousBlock.current_hash != newBlock.previous_hash:
        print('invalid previous_hash')
        return False
    elif not isValidTimestamp(newBlock, previousBlock):
        print('invalid timestamp')
        return False
    elif not hasValidHash(newBlock):
        return False
    return True

def isValidTimestamp(newBlock, previousBlock):
    return ( previousBlock.timestamp - 60 < newBlock.timestamp ) and (newBlock.timestamp - 60 < int(time.time()))

def hasValidHash(block):
    if not hashMatchesBlockContent(block):
        print('invalid hash, got:' + block.current_hash)
        return False
    if not isBlockStakingValid(block.previous_hash, block.timestamp, block.minterBalance, block.difficulty, block.index):
        print('staking hash not lower than balance over diffculty times 2^256')
    return True

def calculateHashForBlock(block):
    sha256 = hashlib.sha256()
    sha256.update((str(block.index) + str(block.timestamp) + str([tx.to_dict() for tx in block.data]) + str(block.previous_hash)+ str(block.minterAddress)+str(block.minterBalance)+str(block.difficulty)).encode('utf-8'))
    sha256_hash = sha256.digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_hash)
    return ripemd160.hexdigest()

def hashMatchesBlockContent(block):
    blockHash = calculateHashForBlock(block)
    return blockHash == block.current_hash

def isBlockStakingValid(prevhash, timestamp, balance, difficulty, index, address=getPublicFromWallet()):
    difficulty = int(difficulty) + 1
    if int(index) <= mintingWithoutCoinIndex:
        balance = int(balance) + 1
    
    balanceOverDifficulty = (float(2) ** 256) * float(balance) / float(difficulty)
    sha256 = hashlib.sha256()
    sha256.update((str(timestamp) + str(prevhash)+ str(address)).encode('utf-8'))
    sha256_hash = sha256.digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_hash)
    stakingHash_temp = ripemd160.hexdigest()
    decimalStakingHash = float(int(stakingHash_temp, 16))

    difference = balanceOverDifficulty - decimalStakingHash
    return difference >= 0

def isValidChain(blockchainToValidate):
    def isValidGenesis(block):
        return block == genesisBlock

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
            updateTransactionPool(getUnspentTxOuts())
            return True
    return False

async def replaceChain(newBlocks):
    aUnspentTxOuts = isValidChain(newBlocks)
    validChain = aUnspentTxOuts != None
    print("replace chain")
    print(validChain)
    print(aUnspentTxOuts)
    if validChain and getAccumulatedDifficulty(newBlocks) > getAccumulatedDifficulty(getBlockchain()):
        print('Received blockchain is valid. Replacing current blockchain with received blockchain')
        blockchain = newBlocks
        setUnspentTxOuts(aUnspentTxOuts)
        updateTransactionPool(unspentTxOuts)
        await broadcastLatest()
    else:
        print('Received blockchain invalid')

def txnFromDict(i):
    tx_ins = [TxIn(txIn['txOutId'], txIn['txOutIndex'], txIn['signature']) for txIn in i['tx_ins']]
    tx_outs = [TxOut(txOut['address'], txOut['amount']) for txOut in i['tx_outs']]
    return Transaction(i['id'], tx_ins, tx_outs)

def blockFromDict(msg):
    data = msg['data']
    for j,i in enumerate(data):
        data[j] = txnFromDict(i)
    return Block(msg['index'], msg['previous_hash'], msg['timestamp'], data, msg['difficulty'], msg['minterBalance'], msg['minterAddress'])


def handleReceivedTransaction(transaction):
    #transaction is coming as a dictionary -> convert to transaction object
    transaction = txnFromDict(transaction)
    addToTransactionPool(transaction, getUnspentTxOuts())