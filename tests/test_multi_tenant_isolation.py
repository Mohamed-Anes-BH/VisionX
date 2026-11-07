import sqlite3
import hashlib
import json
import pytest

def test_full_isolation_and_constraints():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON;")
    
    with open("/home/anes/Documents/VisionX/agent-marketing-automation/schema.sql") as f:
        con.executescript(f.read())
        
    cur = con.cursor()
    
    # 1. Création de deux tenants distincts
    cur.execute("INSERT INTO tenants (id, name, api_key_hash) VALUES (?, ?, ?)", 
                ("company_alpha", "Alpha Corp", "hash_alpha"))
    cur.execute("INSERT INTO tenants (id, name, api_key_hash) VALUES (?, ?, ?)", 
                ("company_beta", "Beta LLC", "hash_beta"))
    
    # Configs
    cur.execute("INSERT INTO tenant_configs (tenant_id) VALUES (?)", ("company_alpha",))
    cur.execute("INSERT INTO tenant_configs (tenant_id) VALUES (?)", ("company_beta",))
    
    # 2. Insertion de prospects
    cur.execute("INSERT INTO prospects (tenant_id, nom, email, score_raw) VALUES (?, ?, ?, ?)",
                ("company_alpha", "Prospect Alpha", "user@alpha.com", 20.0))
    p_alpha_id = cur.lastrowid
    
    cur.execute("INSERT INTO prospects (tenant_id, nom, email, score_raw) VALUES (?, ?, ?, ?)",
                ("company_beta", "Prospect Beta", "user@beta.com", 15.0))
    p_beta_id = cur.lastrowid
    
    # 3. TEST D'ISOLATION CROISÉE : Tenter d'insérer une activité sous company_beta avec le prospect de company_alpha
    # DOIT ÉCHOUER (Violation de clé étrangère composite (tenant_id, prospect_id))
    cross_tenant_failed = False
    try:
        cur.execute("""
            INSERT INTO activities (tenant_id, prospect_id, event_type, points, idempotency_key, occurred_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, ("company_beta", p_alpha_id, "email_click", 10.0, "key_invalid_cross"))
    except sqlite3.IntegrityError as e:
        cross_tenant_failed = True
        print("✔ Isolation stricte validée : Tentative d'association inter-tenant bloquée par FK composite !")
    assert cross_tenant_failed, "Erreur de sécurité : L'association inter-tenant aurait dû être rejetée !"

    # 4. Insertion d'activité valide
    cur.execute("""
        INSERT INTO activities (tenant_id, prospect_id, event_type, points, idempotency_key, occurred_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, ("company_alpha", p_alpha_id, "email_click", 10.0, "key_valid_1"))

    # Test d'idempotence d'activité (même clé) -> DOIT ÉCHOUER
    duplicate_act_failed = False
    try:
        cur.execute("""
            INSERT INTO activities (tenant_id, prospect_id, event_type, points, idempotency_key, occurred_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, ("company_alpha", p_alpha_id, "email_click", 10.0, "key_valid_1"))
    except sqlite3.IntegrityError:
        duplicate_act_failed = True
        print("✔ Idempotence d'activité validée : Clé en double rejetée !")
    assert duplicate_act_failed

    # 5. Gestion des commandes et historique order_events
    cur.execute("""
        INSERT INTO orders (tenant_id, numero_commande, client_email, status, montant_total_ht, payload)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("company_alpha", "CMD-001", "user@alpha.com", "confirmee", 500.0, json.dumps({"items": ["item1"]})))
    ord_id = cur.lastrowid
    
    # Événement 1 : commande confirmée
    cur.execute("""
        INSERT INTO order_events (tenant_id, order_id, numero_commande, status, idempotency_key, payload, occurred_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, ("company_alpha", ord_id, "CMD-001", "confirmee", "evt_cmd1_conf", json.dumps({"status": "confirmee"})))
    
    # Test d'idempotence sur order_events (même idempotency_key) -> DOIT ÉCHOUER
    duplicate_ord_evt = False
    try:
        cur.execute("""
            INSERT INTO order_events (tenant_id, order_id, numero_commande, status, idempotency_key, payload, occurred_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, ("company_alpha", ord_id, "CMD-001", "confirmee", "evt_cmd1_conf", json.dumps({"status": "confirmee"})))
    except sqlite3.IntegrityError:
        duplicate_ord_evt = True
        print("✔ Idempotence des événements de commande validée !")
    assert duplicate_ord_evt

    # 6. Test Outbox & Verrouillage atomique
    cur.execute("""
        INSERT INTO outbox_events (tenant_id, event_type, payload, status)
        VALUES (?, ?, ?, 'PENDING')
    """, ("company_alpha", "prospect_qualified", json.dumps({"id": p_alpha_id, "score": 85})))
    outbox_id = cur.lastrowid
    
    # Simulation d'acquisition atomique par un worker
    cur.execute("""
        UPDATE outbox_events
        SET status = 'PROCESSING', locked_by = 'worker_node_1', locked_until = datetime('now', '+60 seconds')
        WHERE id = ? AND status = 'PENDING'
    """, (outbox_id,))
    assert cur.rowcount == 1, "Le verrouillage atomique aurait dû affecter 1 ligne"
    print("✔ Verrouillage atomique de l'Outbox validé !")

    # 7. TEST DE PURGE ATOMIQUE & ÉTANCHÉITÉ
    # Vérification présence des lignes d'Alpha avant purge
    cur.execute("SELECT COUNT(*) FROM prospects WHERE tenant_id = 'company_alpha'")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM activities WHERE tenant_id = 'company_alpha'")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM orders WHERE tenant_id = 'company_alpha'")
    assert cur.fetchone()[0] == 1
    
    # Exécution de la purge d'Alpha
    cur.execute("DELETE FROM tenants WHERE id = 'company_alpha'")
    
    # Enregistrement de l'audit anonyme (Hash SHA-256 sans PII)
    salt = "VisionX_Audit_Salt_2026"
    t_hash = hashlib.sha256(("company_alpha" + salt).encode()).hexdigest()
    cur.execute("""
        INSERT INTO tenant_purge_audit (tenant_hash, records_deleted, status, executed_by)
        VALUES (?, ?, 'SUCCESS', 'Kernel_API_Webhook')
    """, (t_hash, 5))
    
    # Vérification : Toutes les tables pour Alpha sont VIDES (0)
    for tbl in ["prospects", "activities", "orders", "order_events", "outbox_events", "tenant_configs"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE tenant_id = 'company_alpha'")
        cnt = cur.fetchone()[0]
        assert cnt == 0, f"Fuite de données résiduelles : la table {tbl} contient encore {cnt} lignes pour company_alpha !"
    print("✔ Purge atomique d'Alpha validée à 100 % (Zéro ligne orpheline) !")
    
    # Vérification : Les données de Beta sont INTÈGRES ET INTACTES (100 %)
    cur.execute("SELECT COUNT(*) FROM tenants WHERE id = 'company_beta'")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM prospects WHERE tenant_id = 'company_beta'")
    assert cur.fetchone()[0] == 1
    print("✔ Étanchéité validée : Les données de Beta sont restées 100 % intactes !")
    
    # Vérification de l'audit anonyme (zéro nom de tenant en clair)
    cur.execute("SELECT tenant_hash FROM tenant_purge_audit")
    saved_hash = cur.fetchone()[0]
    assert saved_hash == t_hash
    assert "company_alpha" not in saved_hash
    print("✔ Audit anonyme de purge validé (Zéro PII) !")

if __name__ == "__main__":
    test_full_isolation_and_constraints()
    print("\n=======================================================")
    print("TOUS LES TESTS D'ISOLATION ET DE SÉCURITÉ SONT VALIDÉS !")
    print("=======================================================")
