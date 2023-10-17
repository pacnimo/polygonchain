import json
import time
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_abi import decode_abi
from web3.exceptions import BlockNotFound

# Constants and ABIs
with open('quickswap_router_address_abi.txt', 'r') as abi_file:
    quickswap_router_abi = json.load(abi_file)

w3 = Web3(HTTPProvider('https://polygon-rpc.com'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
quickswap_router_address = '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
SWAP_SIGNATURE = w3.keccak(text="swapExactTokensForTokens(uint256,uint256,address[],address,uint256)").hex()[:10]

def get_symbol(token_address):
    # Using a generic ERC20 ABI for fetching the token symbol
    ERC20_ABI = [{
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }]
    token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
    return token_contract.functions.symbol().call()

def get_latest_swap_transaction():
    # Debug: Print latest block number
    latest_block_number = w3.eth.blockNumber
    print(f"Latest Block Number: {latest_block_number}")

    for block_number in range(latest_block_number, max(0, latest_block_number - 100), -1):  # Adjust range as needed
        print(f"Checking block: {block_number}")
        try:
            block = w3.eth.getBlock(block_number, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] and tx['to'].lower() == quickswap_router_address.lower() and tx['input'].startswith(SWAP_SIGNATURE):
                    print(f"Found swap transaction in block {block_number}: {tx['hash']}")
                    return tx
        except BlockNotFound:
            print(f"Block {block_number} not found. Skipping...")
            continue
    return None

def extract_tokens_and_store():
    swap_counts = {}  # To store token pair counts

    # Try to load existing swap_counts from the JSON file if it exists
    try:
        with open("swap_counts.json", "r") as f:
            swap_counts = json.load(f)
    except FileNotFoundError:
        pass

    while True:
        latest_swap_tx = get_latest_swap_transaction()
        if latest_swap_tx:
            # Decode the input data of the observed transaction to extract token addresses
            input_data = latest_swap_tx['input'][10:]
            types = ['uint256', 'uint256', 'address[]', 'address', 'uint256']
            decoded_data = decode_abi(types, bytes.fromhex(input_data))
            path = decoded_data[2]
            from_token_address = w3.toChecksumAddress(path[0])
            to_token_address = w3.toChecksumAddress(path[1])
            
            # Now, get their symbols
            from_token_symbol = get_symbol(from_token_address)
            to_token_symbol = get_symbol(to_token_address)
            
            # Update the swap_counts
            key = f"{from_token_symbol} -> {to_token_symbol}"
            swap_counts[key] = swap_counts.get(key, 0) + 1

            # Print the fetched data for debugging/observation
            print(f"Swapped: {from_token_symbol} -> {to_token_symbol}")
            print(f"Current Counts: {swap_counts}")

            # Store the swap_counts in a JSON file
            with open("swap_counts.json", "w") as f:
                json.dump(swap_counts, f)

        else:
            print('No swap transaction found. Retrying in 5 seconds...')
            
        time.sleep(5)

if __name__ == '__main__':
    extract_tokens_and_store()
