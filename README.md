# Salcoin

Salcoin is a Proof of Stake (PoS) consensus-based blockchain network written in Python. This project aims to provide a python based implementaion of PoS blockchain network with features like explorer, transaction management and user wallet management.

## Table of Contents

- [Salcoin](#salcoin)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Node](#running-the-node)
    - [API Endpoints](#api-endpoints)
  - [Project Structure](#project-structure)
  - [Undergoing Work](#undergoing-work)

## Introduction

Salcoin is designed to understand the concept of blockchain technology, including transaction handling, consensus mechanisms, peer-to-peer communication, and wallet management. The network uses Proof of Stake for its consensus, providing an efficient and secure method of maintaining the blockchain.

## Features

- **Proof of Stake Consensus**: Efficient and secure block validation mechanism.
- **Wallet Management**: Generate and manage wallets.
- **Transaction Handling**: Create and broadcast transactions.
- **Blockchain Management**: View and interact with the blockchain.
- **Peer-to-Peer Communication**: Connect and sync with peers.

## Installation

To install and run Salcoin, follow these steps:

1. **Clone the repository:**

   ```sh
   git clone https://github.com/SalientPharaoh/SALCoin.git
   cd salcoin
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the Node

To run the blockchain node, run the following commands:

1. **Set the environment variable for the port:**

   ```sh
   export UVICORN_PORT=8000
   ```

2. **Run the server:**

   ```sh
   uvicorn app:app
   ```

### API Endpoints

Salcoin provides a set of API endpoints to interact with the blockchain network. Below is a summary of the available endpoints:

- Get All Blocks: GET /blocks
- Get Latest Block: GET /latestBlock
- Get Block by Hash: GET /block/{hash}
- Get Transaction by ID: GET /transaction/{id}
- Get Unspent Transaction Outputs for Address: GET /address/{address}
- Get All Unspent Transaction Outputs: GET /unspentTransactionOutputs
- Get My Unspent Transaction Outputs: GET /myUnspentTransactionOutputs
- Mint Block: POST /mintBlock
- Get Account Balance: GET /balance
- Get Wallet Address: GET /address
- Mint Transaction: POST /mintTransaction
- Send Transaction: POST /sendTransaction
- Get Transaction Pool: GET /transactionPool
- Get Peers: GET /peers
- Add Peer: POST /addPeer
- Stop Server: POST /stop

For detailed documentation of the API endpoints, refer to the [API Documentation](/docs/API.md).

## Project Structure

```sh
salcoin/
├── main.py                  # Entry point of the application
├── requirements.txt         # Python dependencies
├── salcoin_block.py         # Blockchain and block-related functions
├── salcoin_communication.py # P2P communication functions
├── salcoin_pool.py          # Transaction pool management
├── salcoin_transaction.py   # Transaction handling functions
├── salcoin_wallets.py       # Wallet management functions
├── README.md                # Project documentation
└── docs/
    └── API.md               # Detailed API documentation
```

## Undergoing Work

- Deployment of the root node on cloud ( creation of RPC for interacting with the chain ).
- Development of Salcoin Explorer to explore the blocks and transactions.
- Developement of platform to experience the blockchain.
- Scaling the number of RPCs nodes.
