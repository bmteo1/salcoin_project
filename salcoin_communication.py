from salcoin_transaction import Transaction
from salcoin_pool import getTransactionPool
import websockets
import asyncio
import json

sockets = []

class MessageType:
    QUERY_LATEST = 0
    QUERY_ALL = 1
    RESPONSE_BLOCKCHAIN = 2
    QUERY_TRANSACTION_POOL = 3
    RESPONSE_TRANSACTION_POOL = 4

class Message:
    def __init__(self, msg_type, data):
        self.type = msg_type
        self.data = data

async def getSocket():
    return sockets


async def initConnection(ws): 
    sockets.append(ws)
    await initMessageHandler(ws)
    await initErrorHandler(ws)
    await write(ws, queryChainLengthMsg())
    await asyncio.sleep(2)
    await broadcast(queryTransactionPoolMsg())

async def jsonToObject(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        print(f'Could not parse received JSON message: {data}')
        return None

def initP2PServer(p2p_port):
    async def handleConnection(ws, path):
        await initConnection(ws)

    server = websockets.serve(handleConnection, 'localhost', p2p_port)
    print(f'Listening websocket Peer to Peer port on: {p2p_port}')
    return server

async def initMessageHandler(ws):
    from salcoin_block import handleReceivedTransaction
    async for data in ws:
        try:
            message = await jsonToObject(data)
            if message is None:
                print(f'Could not parse received JSON message: {data}')
                continue
            if message['type'] == MessageType.QUERY_LATEST:
                await write(ws, responseLatestMsg())
            elif message['type'] == MessageType.QUERY_ALL:
                await write(ws, response_chain_msg())
            elif message['type'] == MessageType.RESPONSE_BLOCKCHAIN:
                received_blocks = await jsonToObject(message['data'])
                if received_blocks is None:
                    print(f'Invalid blocks received: {message["data"]}')
                    continue
                await handleBlockchainResponse(received_blocks)
            elif message['type'] == MessageType.QUERY_TRANSACTION_POOL:
                await write(ws, responseTransactionPoolMsg())
            elif message['type'] == MessageType.RESPONSE_TRANSACTION_POOL:
                received_transactions = await jsonToObject(message['data'])
                if received_transactions is None:
                    print(f'Invalid transaction received: {message["data"]}')
                    continue
                for transaction in received_transactions:
                    try:
                        handleReceivedTransaction(transaction)
                        await broadcastTransactionPool()
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)


async def write(ws, message):
    await ws.send(json.dumps(message.__dict__))

async def broadcast(message):
    for socket in sockets:
        await write(socket, message)

def queryChainLengthMsg():
    return Message(MessageType.QUERY_LATEST, None)

def queryAllMsg():
    return Message(MessageType.QUERY_ALL, None)

def response_chain_msg():
    from salcoin_block import getBlockchain
    return Message(MessageType.RESPONSE_BLOCKCHAIN, json.dumps([block.to_dict() for block in getBlockchain()]))

def responseLatestMsg():
    from salcoin_block import getLatestBlock
    return Message(MessageType.RESPONSE_BLOCKCHAIN, json.dumps([getLatestBlock().to_dict()]))

def queryTransactionPoolMsg():
    return Message(MessageType.QUERY_TRANSACTION_POOL, None)

def responseTransactionPoolMsg():
    return Message(MessageType.RESPONSE_TRANSACTION_POOL, json.dumps([tx.to_dict() for tx in getTransactionPool()]))

async def initErrorHandler(ws):
    async def closeConnection():
        print(f'Connection failed to peer: {ws.remote_address}')
        sockets.remove(ws)
    ws.on('close', closeConnection)
    ws.on('error', closeConnection)

async def handleBlockchainResponse(received_blocks):
    from salcoin_block import getLatestBlock, isValidBlockStructure, addBlockToChain, replaceChain, blockFromDict
    if len(received_blocks) == 0:
        print('Received block chain size of 0')
        return

    latestBlockReceived = blockFromDict(received_blocks[-1])
    if not isValidBlockStructure(latestBlockReceived):
        print('Block structure not valid')
        return

    latestBlockHeld = getLatestBlock()

    if latestBlockReceived.index > latestBlockHeld.index:
        print(f'Blockchain possibly behind. We got: {latestBlockHeld.index} Peer got: {latestBlockReceived.index}')
        if latestBlockHeld.current_hash == latestBlockReceived.previous_hash:
            print('Appending received block to local chain')
            if addBlockToChain(latestBlockReceived):
                await broadcast(responseLatestMsg())
        elif len(received_blocks) == 1:
            print('We have to query the chain from our peer')
            await broadcast(queryAllMsg())
        else:
            print('Received blockchain is longer than current blockchain')
            receivedBlocks = [blockFromDict(block) for block in received_blocks]
            await replaceChain(receivedBlocks)
    else:
        print('Received blockchain is not longer than received blockchain.')

async def broadcastLatest():
    await broadcast(responseLatestMsg())

async def connectToPeers(new_peer):
    peer_url = f'ws://{new_peer}'
    asyncio.create_task(connect(peer_url))

async def connect(new_peer):
    try:
        async with websockets.connect(new_peer) as ws:
            await initConnection(ws)
    except Exception as e:
        print(f'Connection failed: {e}')

async def broadcastTransactionPool():
    await broadcast(responseTransactionPoolMsg())
