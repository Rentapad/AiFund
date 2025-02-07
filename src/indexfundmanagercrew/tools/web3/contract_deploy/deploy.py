from web3 import Web3
from eth_account import Account
import json
import os
from pathlib import Path
import click
from typing import Optional, Dict, Any

def load_contract(contract_path: str) -> Dict[str, Any]:
    """Load contract ABI and bytecode from compilation artifacts."""
    with open(contract_path) as f:
        return json.load(f)

def connect_web3(network: str, fork_url: Optional[str] = None) -> Web3:
    """Connect to specified network or fork."""
    # Add your RPC URLs here
    RPC_URLS = {
        'mainnet': os.getenv('ETH_MAINNET_RPC', 'https://eth-mainnet.g.alchemy.com/v2/your-api-key'),
        'goerli': os.getenv('ETH_GOERLI_RPC', 'https://eth-goerli.g.alchemy.com/v2/your-api-key'),
        'sepolia': os.getenv('ETH_SEPOLIA_RPC', 'https://eth-sepolia.g.alchemy.com/v2/your-api-key'),
        'polygon': os.getenv('POLYGON_RPC', 'https://polygon-mainnet.g.alchemy.com/v2/your-api-key'),
        'mumbai': os.getenv('POLYGON_MUMBAI_RPC', 'https://polygon-mumbai.g.alchemy.com/v2/your-api-key'),
        'base': os.getenv('BASE_RPC', 'https://base-mainnet.g.alchemy.com/v2/your-api-key'),
        'base-goerli': os.getenv('BASE_GOERLI_RPC', 'https://base-goerli.g.alchemy.com/v2/your-api-key'),
    }
    
    # If fork URL is provided, use it instead
    if fork_url:
        return Web3(Web3.HTTPProvider(fork_url))
    
    if network not in RPC_URLS:
        raise ValueError(f"Unsupported network: {network}")
    
    return Web3(Web3.HTTPProvider(RPC_URLS[network]))

def deploy_contract(
    w3: Web3,
    private_key: str,
    contract_path: str,
    constructor_args: list = None,
    gas_price_gwei: Optional[float] = None,
    gas_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Deploy a smart contract to the network.
    
    Args:
        w3: Web3 instance
        private_key: Deployer's private key
        contract_path: Path to contract JSON artifact
        constructor_args: Constructor arguments if any
        gas_price_gwei: Gas price in Gwei (optional)
        gas_limit: Gas limit (optional)
    
    Returns:
        Dict with deployment information
    """
    # Load account
    account = Account.from_key(private_key)
    
    # Load contract
    contract_data = load_contract(contract_path)
    contract_name = Path(contract_path).stem
    
    # Create contract object
    contract = w3.eth.contract(
        abi=contract_data['abi'],
        bytecode=contract_data['bytecode']
    )
    
    # Prepare constructor arguments
    if constructor_args is None:
        constructor_args = []
    
    # Prepare deployment transaction
    construct_txn = contract.constructor(*constructor_args).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas_limit or 2000000,  # Default gas limit
        'gasPrice': w3.to_wei(gas_price_gwei or w3.eth.gas_price / 1e9, 'gwei')
    })
    
    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(construct_txn, private_key)
    
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    
    print(f"Contract deployed at: {contract_address}")
    
    # Save deployment info
    deployment_info = {
        'contract_name': contract_name,
        'contract_address': contract_address,
        'deployer_address': account.address,
        'transaction_hash': tx_hash.hex(),
        'block_number': tx_receipt.blockNumber,
        'constructor_args': constructor_args,
        'network': w3.eth.chain_id,
        'gas_used': tx_receipt.gasUsed,
        'gas_price': w3.from_wei(construct_txn['gasPrice'], 'gwei'),
    }
    
    # Save deployment artifacts
    os.makedirs('deployments', exist_ok=True)
    deployment_file = f'deployments/{contract_name}_deployment.json'
    with open(deployment_file, 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    return deployment_info

@click.command()
@click.option('--network', required=True, help='Network to deploy to (mainnet/goerli/sepolia/polygon/mumbai/base/base-goerli)')
@click.option('--contract', required=True, help='Path to contract JSON artifact')
@click.option('--private-key', required=True, help='Private key for deployment')
@click.option('--gas-price', type=float, help='Gas price in Gwei')
@click.option('--gas-limit', type=int, help='Gas limit for deployment')
@click.option('--args', multiple=True, help='Constructor arguments')
@click.option('--fork-url', help='URL for forked network (optional)')
def main(network: str, contract: str, private_key: str, gas_price: float, gas_limit: int, args: tuple, fork_url: str):
    """Deploy a smart contract to the specified network or fork."""
    try:
        # Connect to network
        w3 = connect_web3(network, fork_url)
        network_name = "forked-" + network if fork_url else network
        print(f"Connected to {network_name}")
        
        # Deploy contract
        deployment_info = deploy_contract(
            w3=w3,
            private_key=private_key,
            contract_path=contract,
            constructor_args=list(args) if args else None,
            gas_price_gwei=gas_price,
            gas_limit=gas_limit
        )
        
        print("\nDeployment successful!")
        print(f"Contract address: {deployment_info['contract_address']}")
        print(f"Transaction hash: {deployment_info['transaction_hash']}")
        print(f"Gas used: {deployment_info['gas_used']}")
        print(f"Deployment info saved to: deployments/{deployment_info['contract_name']}_deployment.json")
        
    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        raise

if __name__ == '__main__':
    main()