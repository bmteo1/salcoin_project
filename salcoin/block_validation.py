"""
Este módulo contém funções para validação de transações de blocos, incluindo
cheques de Prova de Participação (PoS) e Prova de História (PoH).
"""

from .transaction_utils import validate_coinbase_tx, validate_transaction, has_duplicates
from .pos import is_valid_validator
from .poh import generate_time_hash, validate_time_hash

def validate_block_transactions(transactions, unspent_tx_outs, block_index, validator_stake):
    """
    Valida as transações do bloco, incluindo verificações de PoS e PoH.
    
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

    # PoS: Verifica a participação do validador
    if not is_valid_validator(validator_stake):
        print('Validator does not have sufficient stake')
        return False

    # PoH: Valida o hash de tempo
    time_hash = generate_time_hash()
    if not validate_time_hash(time_hash):
        print('PoH validation failed')
        return False

    tx_ins = [tx['tx_ins'] for tx in transactions]
    flat_tx_ins = [item for sublist in tx_ins for item in sublist]  # Flatten the list
    if has_duplicates(flat_tx_ins):
        return False

    transacoes_normais = transactions[1:]
    validacoes = [validate_transaction(tx, unspent_tx_outs) for tx in transacoes_normais]

    return all(validacoes)
