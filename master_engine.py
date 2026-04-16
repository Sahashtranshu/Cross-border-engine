import os
import requests
import random
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from web3 import Web3

# 1. SETUP
load_dotenv()
alchemy_url = os.getenv("ALCHEMY_RPC_URL")
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# Tell Flask where to look for the HTML files
app = Flask(__name__, template_folder='templates')

# =========================================================
# THE PRICE ORACLE (Live Market Data)
# =========================================================
def get_live_rates():
    print("\n🔄 [ORACLE]: Fetching live fiat exchange rates from global markets...")
    try:
        # Pinging a public, real-time exchange rate API
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        
        # Extracting the exact pairs we need
        live_mxn = data['rates']['MXN']
        live_inr = data['rates']['INR']
        
        print(f"📡 [ORACLE LIVE]: 1 USD = {live_mxn} MXN | 1 USD = {live_inr} INR")
        return live_mxn, live_inr
        
    except Exception as e:
        # A true financial engine always has a fallback if the API goes down
        print(f"⚠️ [ORACLE ERROR]: {e}. Falling back to safe static rates.")
        return 17.23, 83.50

# 2. CORE LOGIC
def find_cheapest_route(usdc_amount):
    network_fees = {
        "Polygon Amoy": round(random.uniform(0.01, 0.08), 3),
        "Arbitrum Sepolia": round(random.uniform(0.10, 0.25), 3),
        "Base Sepolia": round(random.uniform(0.05, 0.15), 3),
        "Ethereum Sepolia": round(random.uniform(4.00, 12.00), 3)
    }
    best_network = min(network_fees, key=network_fees.get)
    lowest_fee = network_fees[best_network]
    net_usdc = round(usdc_amount - lowest_fee, 2)
    return best_network, lowest_fee, net_usdc

def trigger_india_payout(net_usdc, upi_id, network_used):
    url = "https://webhook.site/7d64f924-eb42-4b68-ace9-1032cbd372b9E" # Replace if you want to check logs
    payload = {
        "amount": net_usdc,
        "currency": "USDC",
        "settlement_network": network_used,
        "destination_fiat": "INR"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Webhook error: {e}")

# 3. FRONTEND ROUTES (The Bridge)
# This serves the UI when you visit the homepage
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('index.html')

# This is the new API door the UI knocks on
@app.route('/api/execute-route', methods=['POST'])
def execute_route():
    data = request.json
    incoming_amount = data.get('amount', 0)
    
    if w3.is_connected():
        # 1. Ping the Oracle for to-the-second market rates
        live_mxn_rate, live_inr_rate = get_live_rates()
        
        # 2. Use the LIVE MXN rate to mint the USDC
        base_usdc = round(incoming_amount / live_mxn_rate, 2)
        
        # 3. Route via cheapest blockchain
        best_network, gas_fee, net_usdc = find_cheapest_route(base_usdc)
        trigger_india_payout(net_usdc, "supplier_name@okicici", best_network)
        
        # 4. Use the LIVE INR rate to calculate the final payout
        estimated_inr = round(net_usdc * live_inr_rate, 2)
        
        return jsonify({
            "status": "success",
            "base_mxn": incoming_amount,
            "base_usdc": base_usdc,
            "winning_network": best_network,
            "network_fee": gas_fee,
            "final_usdc": net_usdc,
            "estimated_inr": estimated_inr
        }), 200
    else:
        return jsonify({"status": "error", "message": "Blockchain offline"}), 500

if __name__ == '__main__':
    # Render provides the port in an environment variable
    port = int(os.environ.get("PORT", 5000))
    print(f"🎧 Startup Dashboard ONLINE. Port {port}...")
    app.run(host="0.0.0.0", port=port)