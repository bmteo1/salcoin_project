# SALCoin API Documentation

## Overview

The SALCoin API provides a set of endpoints to interact with the SALCoin blockchain network. This includes accessing blockchain data, managing transactions, and handling peer connections. Below is the detailed documentation of the available endpoints.

## Base URL

(To be updated Soon)

## Endpoints

### Get All Blocks

- **Endpoint:** `/blocks`
- **Method:** `GET`
- **Response:**

  ```json
  [
    {
      "index": "int",
      "previous_hash": "str",
      "timestamp": "int",
      "data": "list",
      "current_hash": "str"
    }
  ]
  ```

### Get Latest Block

- **Endpoint:** `/latestBlock`
- **Method:** `GET`
- **Response:**

  ```json
  {
  "index": "int",
  "previous_hash": "str",
  "timestamp": "int",
  "data": "list",
  "current_hash": "str"
  }
  ```

### Get Block by Hash

- **Endpoint:** `/block/{hash}`
- **Method:** `GET`
- **Path Parameter:**
- - `hash` : The hash of the block to retrieve.
- **Response:**

  ```json
  {
  "index": "int",
  "previous_hash": "str",
  "timestamp": "int",
  "data": "list",
  "current_hash": "str"
  }
  ```

### Get Transaction by ID

- **Endpoint:** `/transaction/{id}`
- **Method:** `GET`
- **Path Parameter:**
- - `id` : The hash of the block to retrieve.
- **Response:**

  ```json
  {
  "id": "str",
  "tx_ins": "list",
  "tx_outs": "list"
  }
  ```

### Get Unspent Transaction Outputs for Address

- **Endpoint:** `/address/{address}`
- **Method:** `GET`
- **Path Parameter:**
- - `address` : The hash of the block to retrieve.
- **Response:**

  ```json
  {
  "unspentTxOuts": [
    {
      "address": "str",
      "amount": "int",
      "tx_out_id": "str",
      "tx_out_index": "int"
    }
  ]
  }
  ```

### Get All Unspent Transaction Outputs

- **Endpoint:** `/unspentTransactionOutputs`
- **Method:** `GET`
- **Response:**

  ```json
  [
  {
    "address": "str",
    "amount": "int",
    "tx_out_id": "str",
    "tx_out_index": "int"
  }
  ]
  ```

### Get My Unspent Transaction Outputs

- **Endpoint:** `/myUnspentTransactionOutputs`
- **Method:** `GET`
- **Response:**

  ```json
  [
  {
    "address": "str",
    "amount": "int",
    "tx_out_id": "str",
    "tx_out_index": "int"
  }
  ]
  ```

### Mint Block

- **Endpoint:** `/mintBlock`
- **Method:** `POST`
- **Response:**

  ```json
  {
  "index": "int",
  "previous_hash": "str",
  "timestamp": "int",
  "data": "list",
  "current_hash": "str"
  }
  ```

### Mint Transaction

- **Endpoint:** `/mintTransaction`
- **Method:** `POST`
- **Request Body:**

```json
{
  "address": "str",
  "amount": "int"
}
```

- **Response:**

  ```json
  {
  "id": "str",
  "tx_ins": "list",
  "tx_outs": "list"
  }
  ```

### Send Transaction

- **Endpoint:** `/sendTransaction`
- **Method:** `POST`
- **Request Body:**

```json
{
  "address": "str",
  "amount": "int"
}
```

- **Response:**

  ```json
  {
  "id": "str",
  "tx_ins": "list",
  "tx_outs": "list"
  }
  ```

### Get Transaction Pool

- **Endpoint:** `/transactionPool`
- **Method:** `GET`
- **Response:**

  ```json
  [{
  "id": "str",
  "tx_ins": "list",
  "tx_outs": "list"
  }]
  ```

### Get Peers

- **Endpoint:** `/peers`
- **Method:** `GET`
- **Response:**

  ```json
  [
  "ip:port"
  ]
  ```

### Add Peers

- **Endpoint:** `/addPeer`
- **Method:** `POST`
- **Request Body:**

```json
{
  "peer": "str"
}
```

- **Response:**

  ```json
  {
    "message":"Peer added successfully"
  }
  ```
