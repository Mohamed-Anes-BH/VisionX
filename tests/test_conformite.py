import sys, os, json, time
sys.path.insert(0, '/home/anes/Documents/VisionX/agent-marketing-automation')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
results = []

def record(test_id, name, method, path, headers, body, expected_code, expected_status):
    start = time.time()
    if method == "GET":
        resp = client.get(path, headers=headers)
    elif method == "POST":
        resp = client.post(path, headers=headers, json=body)
    duration_ms = round((time.time() - start) * 1000, 2)
    
    passed = (resp.status_code == expected_code)
    try:
        data = resp.json()
        if expected_status:
            passed = passed and (data.get("status") == expected_status)
    except:
        data = resp.text
        
    res = {
        "id": test_id,
        "nom": name,
        "methode": method,
        "chemin": path,
        "headers": headers,
        "corps_envoye": body,
        "code_obtenu": resp.status_code,
        "code_attendu": expected_code,
        "reponse": data,
        "duree_ms": duration_ms,
        "succes": passed
    }
    results.append(res)
    status_icon = "✅" if passed else "❌"
    print(f"{status_icon} [{test_id}] {name} (HTTP {resp.status_code} - {duration_ms}ms)")
    return res

print("\n" + "="*70)
print("  EXÉCUTION DE LA SUITE DE TESTS DE CONFORMITÉ VISIONX (V1.1)")
print("="*70 + "\n")

# 1. Tests Positifs des Routes Obligatoires
record("TEST-01", "Healthcheck standard", "GET", "/health", None, None, 200, "ok")
record("TEST-02", "Schéma de configuration JSON", "GET", "/config-schema", None, None, 200, "ok")
record("TEST-03", "Activation Tenant légitime", "POST", "/tenant/activate", 
       {"X-Tenant-Id": "ENT-ESTIN-01", "Authorization": "Bearer secret-token-xyz"}, 
       {"config": {"seuil_qualification_lead": 75, "auto_email_bienvenue": True}}, 200, "ok")
record("TEST-04", "Statut d'un Tenant actif", "GET", "/tenant/ENT-ESTIN-01/status", None, None, 200, "ok")

# 2. Tests Négatifs et Cas Limites (Exigences de Sécurité & Robustesse)
record("TEST-05", "Activation refusée sans X-Tenant-Id", "POST", "/tenant/activate", 
       None, {"config": {}}, 400, None)
record("TEST-06", "Statut refusé pour Tenant inexistant", "GET", "/tenant/TENANT-INCONNU/status", 
       None, None, 404, None)
record("TEST-07", "Consommation refusée sans X-Tenant-Id", "POST", "/exchange/notify", 
       None, {"object_type": "commande"}, 400, None)
record("TEST-08", "Consommation refusée pour Tenant non activé", "POST", "/exchange/notify", 
       {"X-Tenant-Id": "ENT-FANTOME"}, {"object_type": "commande"}, 404, None)

# 3. Tests Métier : Consommation Commande (Confirmée vs Annulée vs Ignorée)
cmd_confirmee = {
    "object_type": "commande",
    "external_id": "CMD-2027-8888",
    "version": 1,
    "payload": {
        "numero_commande": "CMD-2027-8888",
        "date_commande": "2027-01-15T12:00:00Z",
        "client": {"nom": "Entreprise Alpha", "email": "alpha@pro.dz"},
        "lignes": [{"sku": "SKU-PROD-01", "quantite": 3, "prix_unitaire_ht": 150.0}],
        "montant_total_ht": 450.0,
        "statut": "confirmee"
    }
}
record("TEST-09", "Réception et traitement Commande Confirmée", "POST", "/exchange/notify", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, cmd_confirmee, 200, "ok")

cmd_annulee = {
    "object_type": "commande",
    "external_id": "CMD-2027-8889",
    "version": 1,
    "payload": {
        "numero_commande": "CMD-2027-8889",
        "date_commande": "2027-01-15T13:00:00Z",
        "client": {"nom": "Entreprise Beta", "email": "beta@pro.dz"},
        "lignes": [{"sku": "SKU-PROD-02", "quantite": 1, "prix_unitaire_ht": 80.0}],
        "montant_total_ht": 80.0,
        "statut": "annulee"
    }
}
record("TEST-10", "Réception et relance Commande Annulée", "POST", "/exchange/notify", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, cmd_annulee, 200, "ok")

cmd_inconnue = {"object_type": "capteur_iot", "external_id": "IOT-99", "payload": {}}
record("TEST-11", "Ignorer silencieusement un objet non consommé", "POST", "/exchange/notify", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, cmd_inconnue, 200, "ok")

# 4. Tests Métier : Création et Qualification de Prospect
prospect_fort = {
    "id_prospect": "PROS-2027-0901",
    "nom": "Amina Saidi",
    "email": "amina.s@entreprise.dz",
    "score_interet": 85,
    "statut": "nouveau"
}
record("TEST-12", "Création Prospect qualifié (score >= seuil)", "POST", "/marketing/prospects", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, prospect_fort, 200, "ok")

prospect_faible = {
    "id_prospect": "PROS-2027-0902",
    "nom": "Yacine Mansouri",
    "email": "yacine@entreprise.dz",
    "score_interet": 40,
    "statut": "nouveau"
}
record("TEST-13", "Création Prospect non qualifié (score < seuil)", "POST", "/marketing/prospects", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, prospect_faible, 200, "ok")

# 5. Test d'Isolation Multi-Tenant et Purge Complète (Désactivation)
record("TEST-14", "Désactivation et Purge des données", "POST", "/tenant/deactivate", 
       {"X-Tenant-Id": "ENT-ESTIN-01"}, None, 200, "ok")
record("TEST-15", "Vérification post-purge (accès impossible)", "GET", "/tenant/ENT-ESTIN-01/status", 
       None, None, 404, None)

out_file = "/home/anes/Documents/VisionX/tests/preuves_validation_v1.1.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "="*70)
print(f"  TOTAL : {len(results)} tests exécutés | SUCCÈS : {sum(1 for r in results if r['succes'])} / {len(results)}")
print(f"  Preuves exportées dans : {out_file}")
print("="*70 + "\n")
