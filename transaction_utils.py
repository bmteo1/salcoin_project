"""
This module contains utility functions for transaction validation in the blockchain.
"""

def validate_coinbase_tx(tx, block_index):
    """
    Validates a coinbase transaction.
    
    Args:
        tx (dict): The coinbase transaction.
        block_index (int): The index of the block.
    
    Returns:
        bool: True if the transaction is valid, False otherwise.
    """
    # Example logic to use the arguments
    if tx is None or block_index < 0:
        return False
    # Additional validation logic for coinbase transaction can be added here
    return True

def has_duplicates(tx_ins):
    """
    Checks for duplicate transactions.
    
    Args:
        tx_ins (list): List of transaction inputs.
    
    Returns:
        bool: True if duplicates are found, False otherwise.
    """
    # Example logic to use the arguments
    if tx_ins is None:
        return False
    return len(tx_ins) != len(set(tx_ins))

def validate_transaction(tx, unspent_tx_outs):
    """
    Validates a normal transaction.
    
    Args:
        tx (dict): The transaction to validate.
        unspent_tx_outs (list): List of unspent transaction outputs.
    
    Returns:
        bool: True if the transaction is valid, False otherwise.
    """
    # Example logic to use the arguments
    if tx is None or unspent_tx_outs is None:
        return False
    # Additional validation logic for transaction can be added here
    return True
