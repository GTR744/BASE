# BASE
BASE n'est pas une aide social, c'est un droit.

# BASE – Revenu Universel Décentralisé

---

## 1️⃣ Résumé exécutif

**BASE** est une crypto-monnaie universelle inspirée de Bitcoin mais conçue pour un **revenu universel**.  

Chaque être humain peut recevoir un flux annuel de BASE dès sa naissance, garantissant un droit économique plutôt qu’une aide.  

**Objectifs principaux :**  
- Redistribution équitable à chaque individu.  
- Sécurité et décentralisation via PoW léger CPU.  
- Transactions rapides, simples et peu énergivores.  
- Système transparent pour éviter toute fraude.

---

## 2️⃣ Motivation

Le système économique actuel repose sur la centralisation et l’émission monétaire contrôlée par les États et les banques. BASE propose :  
- Une monnaie qui **garantit à tous un revenu minimal**, indépendamment du statut social.  
- Une alternative décentralisée à l’argent fiduciaire.  
- Une intégration facile dans les services et biens réels.  

---

## 3️⃣ Concept technique

### 3.1 Architecture

- **Layer 1 – Blockchain** : sécurité, minage léger (CPU), ajout de blocs.  
- **Layer 2 – Transactions** : transferts entre wallets avec frais minimes.  
- **Flux universel** : distribution automatique aux wallets selon l’âge.  

### 3.2 Flux universel

| Catégorie | Flux par cycle | Cycle | % utilisable |
|-----------|----------------|-------|--------------|
| Adulte    | 1500 B         | 1 mois| 80 %         |
| Enfant    | 750 B          | 1 mois| 50 %         |

- Blocage des fonds jusqu’à 18 ans pour certains montants.  
- Objectif : permettre à chacun de **vivre grâce à BASE**.  

### 3.3 Transactions et frais

- Frais totaux : 0.075 % par transaction  
  - 0.025 % récompense créateur à vie  
  - 0.05 % frais infrastructure  
- Transactions signées avec **Ed25519** pour sécurité.  
- Transferts rapides, peu énergivores, validés par PoW léger CPU.

### 3.4 Découverte et réseau

- **Peer discovery automatique** via `bootstrap.json` (ou serveur central en production).  
- Synchronisation automatique des blocs et transactions.  
- Multi-node pour résilience et décentralisation.  

---

## 4️⃣ Simulation économique

- Chaque humain actif reçoit son flux BASE à activation (naissance + 18 ans).  
- Flux limité pour éviter surconsommation et inflation.  
- Répartition et blocage conçus pour :  
  - Éviter accumulation massive par fraude.  
  - Garantir que tout le monde puisse **vivre de BASE**.  
- La valeur stable est calibrée sur le **coût de la vie local** : ex. 1 BASE ≈ 1 unité monétaire locale pour biens essentiels.  

---

## 5️⃣ Sécurité et prévention de fraude

- PoW léger CPU empêche le spam et attaques simples.  
- Wallets uniques + clés Ed25519 pour signatures.  
- Flux universel limité par cycle et âge.  
- Blocage des fonds jusqu’à 18 ans pour éviter multi-comptes.  
- Frais minimes pour maintenir l’infrastructure et récompenser le réseau.  

---

## 6️⃣ Déploiement et roadmap

### Phase 1 : Test local  

- Nodes sur PC ou VPS pour validation du réseau et flux universel.  
- Simulation multi-node avec population fictive.  

### Phase 2 : Test public  

- Lancement de quelques nodes publics pour test réseau.  
- Validation transactions et discovery automatique.  

### Phase 3 : Lancement global  

- Publication sur GitHub / site officiel  
- Documentation complète et API publique  
- Applications de paiement et intégration avec biens/services  

---

## 7️⃣ Instructions pour lancer le node

**Installation des dépendances :**

```bash
python -m pip install flask pynacl waitress

python BASE_PUBLIC_NODE.py --port 5000

BASE/
│
├─ README.md            # White Paper complet
├─ BASE_PUBLIC_NODE.py   # Node opérationnel avec découverte auto
├─ bootstrap.json        # Créé automatiquement pour peer discovery
├─ wallet_data.json      # Wallets et clés
├─ blockchaindata.json   # Stockage blockchain
├─ docs/
│   ├─ schema_layer1.png
│   ├─ schema_layer2.png
│   └─ flux_universel.png
└─ examples/
    └─ api_examples.md
