## BASE Crypto Node

BASE est une blockchain simple avec un système de wallets, flux automatique mensuel, et UI web pour consulter solde et historique. Chaque utilisateur peut créer un wallet et envoyer des BASE à d’autres utilisateurs.

## 🚀 Fonctionnalités principales

Flux automatique dès la création du wallet.

Passage automatique child → ado → adult.

Transactions simples et visibles via l’UI.

Backups automatiques des 10 derniers cycles.

Node public prêt pour plusieurs utilisateurs.

## 📦 Installation

Cloner le repo :

git clone https://github.com/TON_UTILISATEUR/BASE.git
cd BASE


Installer les dépendances :

pip install flask pynacl waitress


Lancer le node :

python Base_Final.py


Le node écoute sur : http://127.0.0.1:5000

## 💰 Créer un wallet
##Méthode API

POST vers /wallet/create :

curl -X POST http://127.0.0.1:5000/wallet/create -H "Content-Type: application/json" -d '{"status":"adult"}'


Réponse :

{
  "wallet": "ID_DU_WALLET",
  "sk": "CLE_PRIVEE_HEX",
  "status": "adult"
}


## sk : clé privée à conserver pour exporter/importer ton wallet.

## Méthode UI

Ouvre :

http://127.0.0.1:5000/wallet/ui/<ID_DU_WALLET>


Voir le solde total, utilisable et bloqué.

Voir l’historique récent des transactions.

## 🔄 Envoyer des BASE

POST vers /tx/send :

curl -X POST http://127.0.0.1:5000/tx/send -H "Content-Type: application/json" -d '{"from":"WALLET1","to":"WALLET2","amount":100}'


Réponse :

{
  "status": "ok",
  "tx": {
    "from": "WALLET1",
    "to": "WALLET2",
    "amount": 100,
    "timestamp": 1234567890.0
  }
}

🌐 Explorer la blockchain

GET /chain :

curl http://127.0.0.1:5000/chain

💾 Exporter/Importer un wallet

Exporter :

curl http://127.0.0.1:5000/wallet/<ID_DU_WALLET>


Importer :

Ajouter ton wallet_id et sk dans un nouveau node :

{
  "wallet": "ID_DU_WALLET",
  "sk": "CLE_PRIVEE_HEX",
  "status": "adult"
}
