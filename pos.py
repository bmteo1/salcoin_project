"""
This module implements basic functionalities for Proof of Stake (PoS) for block validation.
"""

# Define the coinbase amount (e.g., 50 tokens)
COINBASE_AMOUNT = 50

# Define the minimum stake for validators
MINIMUM_STAKE = 50  # Example minimum stake amount

def is_valid_validator(validator_stake):
    """
    Checks if the validator has the minimum required stake.
    
    Args:
        validator_stake (int): Amount of tokens staked by the validator.
    
    Returns:
        bool: True if the stake is sufficient, False otherwise.
    """
    return validator_stake >= MINIMUM_STAKE

def distribute_staking_rewards(validators, total_stake):
    """
    Distributes staking rewards among validators.
    
    Args:
        validators (list): List of validators with their stakes and balances.
        total_stake (int): Total amount of tokens staked.
    """
    for validator in validators:
        reward = COINBASE_AMOUNT * (validator['stake'] / total_stake)
        validator['balance'] += reward

# Example usage of the functions
validator_list = [
    {'stake': 100, 'balance': 0},
    {'stake': 200, 'balance': 0},
]
total_stake_amount = sum(validator['stake'] for validator in validator_list)
distribute_staking_rewards(validator_list, total_stake_amount)
print(validator_list)
