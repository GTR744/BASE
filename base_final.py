import os, json, time, hashlib
from threading import Thread
from flask import Flask, request, jsonify, render_template_string
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from waitress import serve

# ==============================
# CONFIGURATION
# ==============================
BLOCK_TIME = 30  # secondes par cycle
SAVE_CYCLES = 10

CHILD_MONTHLY = 750
ADO_MONTHLY = 1000
ADULT_MONTHLY = 1500

CHILD_USABLE = 0.5
ADO_USABLE = 0.6
ADULT_USABLE = 0.8

DATA_CHAIN = "blockchain.json"
DATA_WALLETS = "wallets.json"
BACKUP_DIR = "backups"

# ==============================
# INIT
# ==============================
app = Flask(__name__)
chain = []
wallets = {}
mempool = []

os.makedirs(BACKUP_DIR, exist_ok=True)

# ==============================
# UTILS
# ==============================
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def save_state():
    with open(DATA_CHAIN, "w") as f:
        json.dump(chain, f, indent=2)
    with open(DATA_WALLETS, "w") as f:
        json.dump(wallets, f, indent=2)

    # Backup rolling
    if chain:
        idx = chain[-1]["index"]
        backup_file = os.path.join(BACKUP_DIR, f"backup_{idx}.json")
        json.dump({"chain": chain, "wallets": wallets}, open(backup_file, "w"), indent=2)
        files = sorted(os.listdir(BACKUP_DIR))
        while len(files) > SAVE_CYCLES:
            os.remove(os.path.join(BACKUP_DIR, files.pop(0)))

def load_state():
    global chain, wallets
    if os.path.exists(DATA_CHAIN):
        chain = json.load(open(DATA_CHAIN))
    if os.path.exists(DATA_WALLETS):
        wallets = json.load(open(DATA_WALLETS))

# ==============================
# BLOCKCHAIN
# ==============================
def genesis():
    if not chain:
        chain.append({
            "index": 0,
            "timestamp": time.time(),
            "transactions": [],
            "prev_hash": "0",
            "hash": "GENESIS"
        })
        save_state()

def mine():
    while True:
        time.sleep(BLOCK_TIME)
        apply_flux_all()
        prev = chain[-1]
        block = {
            "index": len(chain),
            "timestamp": time.time(),
            "transactions": mempool.copy(),
            "prev_hash": prev["hash"]
        }
        block["hash"] = sha256(json.dumps(block, sort_keys=True))
        chain.append(block)
        mempool.clear()
        save_state()
        print(f"[MINED] Bloc {block['index']}")

# ==============================
# WALLET ECONOMY
# ==============================
def apply_flux(wallet_id):
    w = wallets[wallet_id]
    month = time.strftime("%Y-%m")
    if w.get("last_month") == month:
        return

    if w["status"] == "child":
        amount, ratio = CHILD_MONTHLY, CHILD_USABLE
    elif w["status"] == "ado":
        amount, ratio = ADO_MONTHLY, ADO_USABLE
    else:
        amount, ratio = ADULT_MONTHLY, ADULT_USABLE

    usable = amount * ratio
    w["balance"] += amount
    w["usable"] += usable
    w["locked"] += amount - usable
    w["age_cycles"] += 1

    # Passage automatique
    if w["status"] == "child" and w["age_cycles"] >= 18:
        w["status"] = "ado"
    elif w["status"] == "ado" and w["age_cycles"] >= 36:
        w["status"] = "adult"

    w["last_month"] = month

def apply_flux_all():
    for wid in wallets:
        apply_flux(wid)
    save_state()

# ==============================
# WALLET CREATION
# ==============================
def generate_wallet(status="adult"):
    sk = SigningKey.generate()
    vk = sk.verify_key.encode(encoder=HexEncoder).decode()
    wallets[vk] = {
        "balance": 0,
        "usable": 0,
        "locked": 0,
        "status": status,
        "age_cycles": 0,
        "last_month": ""
    }
    apply_flux(vk)
    save_state()
    return vk, sk.encode(encoder=HexEncoder).decode()

# ==============================
# TRANSACTIONS
# ==============================
def create_transaction(sender, receiver, amount):
    if sender not in wallets or receiver not in wallets:
        return {"error": "wallet inconnu"}
    if wallets[sender]["usable"] < amount:
        return {"error": "fonds insuffisants"}
    wallets[sender]["usable"] -= amount
    wallets[sender]["balance"] -= amount
    wallets[receiver]["balance"] += amount
    wallets[receiver]["usable"] += amount
    tx = {
        "from": sender,
        "to": receiver,
        "amount": round(amount,2),
        "timestamp": time.time()
    }
    mempool.append(tx)
    save_state()
    return {"status": "ok", "tx": tx}

# ==============================
# API ROUTES
# ==============================
@app.route("/wallet/create", methods=["POST"])
def api_create_wallet():
    data = request.json or {}
    status = data.get("status", "adult")
    vk, sk = generate_wallet(status)
    return jsonify({"wallet": vk, "sk": sk, "status": status})

@app.route("/wallet/<wid>", methods=["GET"])
def api_wallet_view(wid):
    if wid not in wallets:
        return jsonify({"error":"wallet inconnu"}), 404
    return jsonify(wallets[wid])

@app.route("/wallet/ui/<wid>", methods=["GET"])
def wallet_ui(wid):
    w = wallets.get(wid)
    if not w:
        return "Wallet inconnu"
    html = """
    <body style="background:#111;color:#0f0;font-family:Arial;padding:20px">
    <h2>BASE Wallet</h2>
    <p>ID: {{ wid }}</p>
    <p>Status: {{ w.status }}</p>
    <p>Solde total: {{ w.balance }}</p>
    <p>Solde utilisable: {{ w.usable }}</p>
    <p>Solde bloqué: {{ w.locked }}</p>
    <h3>Historique récent</h3>
    <ul>
    {% for tx in history %}
      <li>{{ tx["from"][:4] }} → {{ tx["to"][:4] }} : {{ tx["amount"] }} BASE</li>
    {% endfor %}
    </ul>
    </body>
    """
    return render_template_string(html, wid=wid, w=w, history=mempool[-10:])

@app.route("/chain", methods=["GET"])
def api_chain():
    return jsonify(chain)

@app.route("/tx/send", methods=["POST"])
def api_send_tx():
    data = request.json
    sender = data["from"]
    receiver = data["to"]
    amount = float(data["amount"])
    return jsonify(create_transaction(sender, receiver, amount))

# ==============================
# LANCEMENT NODE
# ==============================
if __name__ == "__main__":
    load_state()
    genesis()
    Thread(target=mine, daemon=True).start()
    print("NODE BASE prêt sur http://127.0.0.1:5000")
    serve(app, host="0.0.0.0", port=5000)
