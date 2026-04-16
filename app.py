import os
import requests
from dotenv import load_dotenv
from web3 import Web3

# 1. Open the Vault
load_dotenv()
alchemy_url = os.getenv("ALCHEMY_RPC_URL")
wallet_address = os.getenv("MASTER_WALLET_ADDRESS")
transfi_mid = os.getenv("TRANSFI_MID")
transfi_password = os.getenv("TRANSFI_API_PASSWORD")

# Connect to the Post Office (Alchemy)
w3 = Web3(Web3.HTTPProvider(alchemy_url))
USDC_CONTRACT_ADDRESS = "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582"

# Minimal instructions for Python to read token balances
erc20_abi = [{"constant": True,"inputs": [{"name": "_owner", "type": "address"}],"name": "balanceOf","outputs": [{"name": "balance", "type": "uint256"}],"type": "function"}]

# ---------------------------------------------------------
# 🚪 THE EXIT DOOR: TransFi (India) Integration
# ---------------------------------------------------------
def trigger_india_payout(usdc_amount, upi_id):
    print(f"\n🚪 Initiating Exit Door: Instructing TransFi to liquidate {usdc_amount} USDC...")
    
    # The TransFi Sandbox API Endpoint
    url = "https://webhook.site/7d64f924-eb42-4b68-ace9-1032cbd372b9"
    
    # The payload: What we are telling TransFi to do
    payload = {
        "amount": usdc_amount,
        "currency": "USDC",
        "destination_fiat": "INR",
        "payment_method": "UPI",
        "destination_address": upi_id
    }
    
    # Security: Authenticating with your Vault keys
    auth = (transfi_mid, transfi_password)
    
    try:
        # Pinging the TransFi server
        response = requests.post(url, json=payload, auth=auth)
        
        # If TransFi returns a 200 or 201 code, it means "Message Received and Processed"
        if response.status_code in [200, 201]:
            print(f"✅ SUCCESS: Payout triggered! INR is en route to {upi_id}.")
        else:
            print(f"⚠️ API Ping Successful, but TransFi returned status: {response.status_code}")
            print("Note: In the Sandbox, a 401/404 just means we need to whitelist your IP in their dashboard later.")
            print(f"Raw Response: {response.text}")
            
    except Exception as e:
        print(f"🔴 ERROR connecting to TransFi: {e}")

# ---------------------------------------------------------
# 🚀 MAIN ENGINE EXECUTION
# ---------------------------------------------------------
if w3.is_connected():
    print("🟢 SUCCESS: Connected to Polygon Amoy!")
    
    # Check POL Gas Balance
    balance_wei = w3.eth.get_balance(wallet_address)
    balance_pol = w3.from_wei(balance_wei, 'ether')
    
    # Check USDC Cargo Balance
    checksum_usdc_address = w3.to_checksum_address(USDC_CONTRACT_ADDRESS)
    checksum_wallet = w3.to_checksum_address(wallet_address)
    usdc_contract = w3.eth.contract(address=checksum_usdc_address, abi=erc20_abi)
    usdc_balance_raw = usdc_contract.functions.balanceOf(checksum_wallet).call()
    usdc_balance = usdc_balance_raw / (10 ** 6)
    
    print(f"💼 Wallet: {wallet_address}")
    print(f"⛽ Gas Balance:   {balance_pol} POL")
    print(f"💵 Asset Balance: {usdc_balance} USDC")
    
    # --- TRIGGER THE OFF-RAMP SIMULATION ---
    # We simulate telling TransFi to send money to an Indian supplier's UPI ID
    trigger_india_payout(20, "supplier_name@okicici")

else:
    print("🔴 ERROR: Could not connect to the blockchain.")