"""
Este módulo contém testes para a função de validação de blocos.
"""

from transaction_utils import (
    validate_coinbase_tx,
    validate_transaction
)  # Adicionar importações necessárias

from pos import is_valid_validator  # Adicionar importações necessárias

from poh import (
    generate_time_hash,
    validate_time_hash
)  # Adicionar importações necessárias

def has_duplicates(tx_ins):
    """
    Verifica se há alguma duplicata nas entradas de transação.
    
    Args:
        tx_ins (list): Lista de entradas de transação.
    
    Returns:
        bool: True se houver duplicatas, False caso contrário.
    """
    seen = set()
    for tx_in in tx_ins:
        tx_in_tuple = tuple(tx_in) if isinstance(tx_in, list) else tx_in
        if tx_in_tuple in seen:
            return True
        seen.add(tx_in_tuple)
    return False

def validate_block_transactions_for_test(
    transactions, unspent_tx_outs, block_index, validator_stake
):
    """
    Função de validação de transações de blocos para testes.
    
    Args:
        transactions (list): Lista de transações no bloco.
        unspent_tx_outs (list): Lista de saídas de transações não gastas.
        block_index (int): Índice do bloco.
        validator_stake (int): Participação do validador.
    
    Returns:
        bool: True se todas as transações forem válidas, False caso contrário.
    """
    coinbase_tx = transactions[0]
    if not validate_coinbase_tx(coinbase_tx, block_index):
        print('Invalid coinbase transaction: ' + str(coinbase_tx))
        return False

    # PoS: Check validator's stake
    if not is_valid_validator(validator_stake):
        print('Validator does not have sufficient stake')
        return False

    # PoH: Validate time hash
    time_hash = generate_time_hash()
    if not validate_time_hash(time_hash):
        print('PoH validation failed')
        return False

    tx_ins = [tx['tx_ins'] for tx in transactions]
    flat_tx_ins = [item for sublist in tx_ins for item in sublist]  # Flatten the list
    if has_duplicates(flat_tx_ins):
        return False

    normal_transactions = transactions[1:]
    validations = [
        validate_transaction(tx, unspent_tx_outs)
        for tx in normal_transactions
    ]

    return all(validations)

def test_block_validation():
    """
    Esta função executa vários testes para validar transações de blocos.
    """
    print("Test 1: Valid Block")
    transactions = [
        {"tx_ins": ["input1", "input2"], "tx_outs": ["output1", "output2"]},
        {"tx_ins": ["input3"], "tx_outs": ["output3"]},
    ]
    unspent_tx_outs = ["output1", "output2", "output3"]
    block_index = 0
    validator_stake = 1000

    result = validate_block_transactions_for_test(
        transactions, unspent_tx_outs, block_index, validator_stake
    )
    print(f"Validation Result: {result}\n")

    print("Test 2: Invalid Coinbase Transaction")
    transactions = [
        {"tx_ins": ["input1", "input2"], "tx_outs": ["output1", "output2"]},
        {"tx_ins": ["input3"], "tx_outs": ["output3"]},
    ]
    unspent_tx_outs = ["output1", "output2"]
    block_index = -1  # Invalid block index
    validator_stake = 1000

    result = validate_block_transactions_for_test(
        transactions, unspent_tx_outs, block_index, validator_stake
    )
    print(f"Validation Result: {result}\n")

    print("Test 3: Insufficient Validator Stake")
    transactions = [
        {"tx_ins": ["input1", "input2"], "tx_outs": ["output1", "output2"]},
        {"tx_ins": ["input3"], "tx_outs": ["output3"]},
    ]
    unspent_tx_outs = ["output1", "output2", "output3"]
    block_index = 0
    validator_stake = 0  # Insufficient stake

    result = validate_block_transactions_for_test(
        transactions, unspent_tx_outs, block_index, validator_stake
    )
    print(f"Validation Result: {result}\n")

    print("Test 4: Duplicate Transactions")
    transactions = [
        {"tx_ins": ["input1", "input1"], "tx_outs": ["output1", "output2"]},
        {"tx_ins": ["input3"], "tx_outs": ["output3"]},
    ]
    unspent_tx_outs = ["output1", "output2", "output3"]
    block_index = 0
    validator_stake = 1000

    flat_tx_ins = [
        item for sublist in transactions
        for item in sublist
    ]  # Flatten the list
    if has_duplicates(flat_tx_ins):
        print("Duplicate transaction inputs found")

    result = validate_block_transactions_for_test(
        transactions, unspent_tx_outs, block_index, validator_stake
    )
    print(f"Validation Result: {result}\n")

if __name__ == "__main__":
    test_block_validation()
