import requests

# Your public VS Code tunnel URL + the specific route you made in listener.py
# Example: "https://g78x...-5000.use.devtunnels.ms/bitso-webhook"
url = "http://127.0.0.1:5000/bitso-webhook"

# The simulated data package Bitso sends when fiat arrives
simulated_payload = {
    "transaction_id": "tx_987654321",
    "currency": "MXN",
    "amount": 10000,
    "status": "completed"
}

print(f"Firing test payload to {url}...")

try:
    response = requests.post(url, json=simulated_payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response from your server: {response.text}")
except Exception as e:
    print(f"Error: {e}")