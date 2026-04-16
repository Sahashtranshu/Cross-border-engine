from flask import Flask, request, jsonify

# Initialize the server
app = Flask(__name__)

# ---------------------------------------------------------
# 📥 THE ENTRANCE DOOR: Listening for the Fiat On-Ramp
# ---------------------------------------------------------
@app.route('/bitso-webhook', methods=['POST'])
def bitso_entrance():
    # 1. Catch the incoming digital package
    data = request.json
    
    print("\n🔔 [ENTRANCE TRIGGERED] Incoming signal received!")
    print(f"📦 Raw Data Package: {data}")
    
    # 2. Extract the important information (simulated)
    # In reality, we will map this to Bitso's exact JSON format later
    asset = data.get('currency', 'UNKNOWN')
    amount = data.get('amount', 0)
    
    print(f"✅ CONFIRMED: {amount} {asset} is minted and ready for routing.")
    print("🚀 Next Step: Triggering the smart contract routing engine...")
    
    # 3. Tell the API partner "Message received loud and clear"
    return jsonify({"status": "success", "message": "Engine starting"}), 200

# ---------------------------------------------------------
# 🎧 START THE SYSTEM
# ---------------------------------------------------------
if __name__ == '__main__':
    print("🎧 Entrance Door is OPEN. Listening for incoming funds on port 5000...")
    # Running on local network
    app.run(host="0.0.0.0", port=5000)