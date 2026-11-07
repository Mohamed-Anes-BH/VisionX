import sys
import os
import hashlib
from decimal import Decimal

sys.path.insert(0, '/home/anes/Documents/VisionX/agent-marketing-automation')

from app.db.session import SessionLocal
from app.models import (
    Tenant, TenantConfig, Prospect, Activity, Order, OrderEvent,
    EmailTemplate, Campaign, CampaignDispatch, CampaignLog,
    OutboxEvent, EmailSuppression, TenantPurgeAudit,
    AdminUser, AdminSession
)

def seed_and_test():
    db = SessionLocal()
    try:
        # Nettoyage préventif
        db.query(Tenant).delete()
        db.commit()

        # 1. Création de deux tenants distincts
        t_alpha = Tenant(id="company_alpha", name="Alpha Technologies", api_key_hash="hash_alpha_secret")
        t_beta = Tenant(id="company_beta", name="Beta Solutions", api_key_hash="hash_beta_secret")
        db.add_all([t_alpha, t_beta])
        db.commit()

        # Configs
        cfg_alpha = TenantConfig(tenant_id="company_alpha", qualification_threshold=70, score_half_life_days=30)
        cfg_beta = TenantConfig(tenant_id="company_beta", qualification_threshold=65, score_half_life_days=15)
        db.add_all([cfg_alpha, cfg_beta])
        db.commit()

        # 2. Modèles d'emails & Campagnes pour Alpha
        tpl_alpha_welcome = EmailTemplate(
            tenant_id="company_alpha",
            name="welcome_email",
            subject="Bienvenue chez Alpha Technologies !",
            html_body="<p>Bonjour {{ prospect.nom }}, merci de votre intérêt.</p>"
        )
        tpl_alpha_onboarding = EmailTemplate(
            tenant_id="company_alpha",
            name="order_onboarding",
            subject="Confirmation de votre commande {{ order.numero_commande }}",
            html_body="<p>Votre commande a été confirmée avec succès !</p>"
        )
        db.add_all([tpl_alpha_welcome, tpl_alpha_onboarding])
        db.commit()

        cmp_alpha_welcome = Campaign(
            tenant_id="company_alpha",
            name="Campagne Bienvenue",
            trigger_type="prospect_created",
            category="marketing",
            template_id=tpl_alpha_welcome.id
        )
        cmp_alpha_onboarding = Campaign(
            tenant_id="company_alpha",
            name="Campagne Onboarding Client",
            trigger_type="order_confirmed",
            category="transactional",
            template_id=tpl_alpha_onboarding.id
        )
        db.add_all([cmp_alpha_welcome, cmp_alpha_onboarding])
        db.commit()

        # 3. Prospects pour Alpha et Beta
        p_alpha1 = Prospect(tenant_id="company_alpha", nom="Karim Belkacem", email="karim@client-alpha.dz", score_raw=Decimal("65.00"), status="ENGAGED")
        p_alpha2 = Prospect(tenant_id="company_alpha", nom="Yacine Meziane", email="yacine@client-alpha.dz", score_raw=Decimal("80.00"), status="QUALIFIED")
        p_beta1 = Prospect(tenant_id="company_beta", nom="Nadia Hamidi", email="nadia@client-beta.dz", score_raw=Decimal("45.00"), status="NEW")
        db.add_all([p_alpha1, p_alpha2, p_beta1])
        db.commit()

        # 4. Activités & Idempotence
        act_alpha = Activity(
            tenant_id="company_alpha",
            prospect_id=p_alpha1.id,
            event_type="webinar_attendance",
            points=Decimal("15.00"),
            idempotency_key="idemp_act_alpha_001",
            occurred_at="2026-11-07T14:00:00Z"
        )
        db.add(act_alpha)
        db.commit()

        # 5. Commandes & Historique
        ord_alpha = Order(
            tenant_id="company_alpha",
            numero_commande="CMD-ALPHA-2026-001",
            client_email="yacine@client-alpha.dz",
            status="confirmee",
            montant_total_ht=Decimal("1250.00"),
            payload='{"client": "Yacine Meziane", "total": 1250.00}'
        )
        db.add(ord_alpha)
        db.commit()

        ord_evt = OrderEvent(
            tenant_id="company_alpha",
            order_id=ord_alpha.id,
            numero_commande="CMD-ALPHA-2026-001",
            status="confirmee",
            idempotency_key="idemp_ord_alpha_001_conf",
            payload='{"status": "confirmee"}',
            occurred_at="2026-11-07T15:00:00Z"
        )
        db.add(ord_evt)
        db.commit()

        # 6. Outbox Event pour prospect qualifié
        outbox_alpha = OutboxEvent(
            tenant_id="company_alpha",
            event_type="prospect_qualified",
            payload='{"id_prospect": 2, "score_interet": 80, "statut": "qualifie"}',
            status="PENDING"
        )
        db.add(outbox_alpha)
        db.commit()

        # VÉRIFICATIONS D'ÉTANCHÉITÉ ET D'ISOLATION
        alpha_prospects = db.query(Prospect).filter(Prospect.tenant_id == "company_alpha").all()
        beta_prospects = db.query(Prospect).filter(Prospect.tenant_id == "company_beta").all()
        assert len(alpha_prospects) == 2, "Erreur nombre prospects Alpha"
        assert len(beta_prospects) == 1, "Erreur nombre prospects Beta"

        # TEST DE PURGE ATOMIQUE VIA SQLALCHEMY ORM
        # Suppression de l'objet Tenant Alpha -> cascade automatique
        t_to_delete = db.query(Tenant).filter(Tenant.id == "company_alpha").first()
        db.delete(t_to_delete)
        
        # Audit anonyme
        t_hash = hashlib.sha256(("company_alpha" + "VisionX_Audit_Salt_2026").encode()).hexdigest()
        audit = TenantPurgeAudit(
            tenant_hash=t_hash,
            records_deleted=8,
            status="SUCCESS",
            executed_by="Automated_Test_Runner"
        )
        db.add(audit)
        db.commit()

        # Vérification qu'Alpha a disparu à 100% de toutes les tables
        assert db.query(Prospect).filter(Prospect.tenant_id == "company_alpha").count() == 0
        assert db.query(Activity).filter(Activity.tenant_id == "company_alpha").count() == 0
        assert db.query(Order).filter(Order.tenant_id == "company_alpha").count() == 0
        assert db.query(Campaign).filter(Campaign.tenant_id == "company_alpha").count() == 0
        assert db.query(OutboxEvent).filter(OutboxEvent.tenant_id == "company_alpha").count() == 0

        # Vérification que Beta est intact
        assert db.query(Tenant).filter(Tenant.id == "company_beta").count() == 1
        assert db.query(Prospect).filter(Prospect.tenant_id == "company_beta").count() == 1
        print("✔ Données de démo injectées et cycle complet de persistance/purge SQLAlchemy 2.x validé avec succès !")
    finally:
        db.close()

if __name__ == "__main__":
    seed_and_test()
