import os, json, time, hashlib
from threading import Thread
from flask import Flask, request, jsonify, render_template_string
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from waitress import serve

# ==============================
# CONFIG
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
# UTIL
# ==============================
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

def save_state():
    with open(DATA_CHAIN, "w") as f:
        json.dump(chain, f, indent=2)
    with open(DATA_WALLETS, "w") as f:
        json.dump(wallets, f, indent=2)

    if chain:
        idx = chain[-1]["index"]
        backup_file = os.path.join(BACKUP_DIR, f"backup_{idx}.json")
        with open(backup_file, "w") as f:
            json.dump({"chain": chain, "wallets": wallets}, f, indent=2)

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
    w["age"] += 1

    # Passage automatique
    if w["status"] == "child" and w["age"] >= 18:
        w["status"] = "ado"
    elif w["status"] == "ado" and w["age"] >= 36:
        w["status"] = "adult"

    w["last_month"] = month

def apply_flux_all():
    for wid in wallets:
        apply_flux(wid)
    save_state()

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
        "hash": sha256(f"{sender}{receiver}{amount}{time.time()}")
    }
    mempool.append(tx)
    save_state()
    return {"status": "ok", "tx": tx}

# ==============================
# WALLET CREATE / EXPORT / IMPORT
# ==============================
@app.route("/wallet/create", methods=["POST"])
def api_create_wallet():
    data = request.json or {}
    status = data.get("status","adult")
    sk = SigningKey.generate()
    vk = sk.verify_key.encode(encoder=HexEncoder).decode()
    wallets[vk] = {
        "status": status,
        "balance": 0,
        "usable": 0,
        "locked": 0,
        "age": 0,
        "last_month": "",
        "sk": sk.encode(encoder=HexEncoder).decode()
    }
    apply_flux(vk)  # flux initial
    save_state()
    return jsonify({"wallet": vk, "sk": wallets[vk]["sk"]})

@app.route("/wallet/export/<wid>")
def api_export_wallet(wid):
    if wid not in wallets:
        return jsonify({"error":"wallet inconnu"}),404
    return jsonify(wallets[wid])

@app.route("/wallet/import", methods=["POST"])
def api_import_wallet():
    data = request.json
    wid = data["wallet"]
    sk = data["sk"]
    status = data.get("status","adult")
    wallets[wid] = {
        "status": status,
        "balance": data.get("balance",0),
        "usable": data.get("usable",0),
        "locked": data.get("locked",0),
        "age": data.get("age",0),
        "last_month": data.get("last_month",""),
        "sk": sk
    }
    save_state()
    return jsonify({"wallet": wid})

# ==============================
# API / UI
# ==============================
@app.route("/wallet/ui/<wid>", methods=["GET","POST"])
def wallet_ui(wid):
    w = wallets.get(wid)
    if not w:
        return "Wallet inconnu"
    if request.method=="POST":
        to = request.form["to"]
        amount = float(request.form["amount"])
        create_transaction(wid,to,amount)

    history = [
        f"{tx['from'][:6]} → {tx['to'][:6]} : {tx['amount']} B"
        for tx in mempool[-10:]
    ]

    html = """
    <body style="background:#111;color:#0f0;font-family:Arial;padding:20px">
    <h2>BASE Wallet</h2>
    <p>ID: {{ wid }}</p>
    <p>Status: {{ w.status }}</p>
    <p>Age: {{ w.age }}</p>
    <p>Solde: {{ w.balance }}</p>
    <p>Utilisable: {{ w.usable }}</p>
    <p>Bloqué: {{ w.locked }}</p>
    <h3>Historique récent</h3>
    <ul>
    {% for tx in history %}
    <li>{{ tx }}</li>
    {% endfor %}
    </ul>
    <h3>Envoyer BASE</h3>
    <form method="post">
    <input name="to" placeholder="Wallet destinataire" required><br>
    <input name="amount" placeholder="Montant" required><br>
    <button type="submit">Envoyer</button>
    </form>
    </body>
    """
    return render_template_string(html,w=w,wid=wid,history=history)

@app.route("/chain")
def view_chain():
    return jsonify(chain)

# ==============================
# RUN
# ==============================
if __name__=="__main__":
    load_state()
    genesis()
    Thread(target=mine,daemon=True).start()
    print("NODE BASE prêt sur http://127.0.0.1:5000")
    serve(app,host="0.0.0.0",port=5000)
