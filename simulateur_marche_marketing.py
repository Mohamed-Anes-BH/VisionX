#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulateur Minimal de Marche Multi-Agents (SMA)
Projet : Agent Metier Marketing & Integration au Noyau
======================================================
Ce script illustre concretement comment votre agent de marketing va interagir 
avec le Noyau du professeur et negocier avec les agents des autres equipes.
Aucune bibliotheque externe requise (standard library pure).
"""

import json

# =====================================================================
# 1. COUCHE METIER MARKETING (Decision Engine)
# =====================================================================
class MarketingStrategy:
    """
    Gestion des prix et regles de negociation purement marketing.
    Isolee de toute logique reseau.
    """
    def __init__(self, cost_price: float, min_margin: float = 1.15, max_margin: float = 1.60):
        self.cost_price = cost_price
        self.p_min = cost_price * min_margin     # Seuil de rentabilite incompressible (57.5€)
        self.p_max = cost_price * max_margin     # Prix d'ouverture ideal (80.0€)

    def compute_target_price(self, progress_ratio: float, beta: float = 1.4) -> float:
        """
        Calcul du prix dynamique cible selon le temps restant dans le tour (0.0 a 1.0).
        beta > 1 : strategie concessionnaire (baisse progressive du prix cible).
        """
        factor = max(0.0, 1.0 - progress_ratio) ** beta
        return round(self.p_min + (self.p_max - self.p_min) * factor, 2)

    def evaluate_buyer_offer(self, offered_price: float, progress_ratio: float):
        """
        Matrice de decision marketing face a une offre d'achat recue.
        """
        target = self.compute_target_price(progress_ratio)
        
        if offered_price >= target:
            # Prix superieur ou egal a notre cible actuelle -> ACCEPTER
            return "ACCEPT_PROPOSAL", offered_price
        elif offered_price >= self.p_min:
            # Prix acceptable mais sous la cible -> Proposer un compromis a mi-chemin
            counter_offer = round((target + offered_price) / 2.0, 2)
            return "PROPOSE", counter_offer
        else:
            # Offre sous le prix plancher de rentabilite -> REFUSER
            return "REJECT_PROPOSAL", None


# =====================================================================
# 2. L'AGENT METIER DE MARKETING DE VOTRE EQUIPE
# =====================================================================
class MarketingAgent:
    """
    Votre Agent : maintient ses croyances (stocks, prix), ecoute les messages
    du noyau et prend des decisions autonomes.
    """
    def __init__(self, agent_id: str, team_name: str, kernel_bus):
        self.agent_id = agent_id
        self.team_name = team_name
        self.kernel = kernel_bus
        self.strategy = MarketingStrategy(cost_price=50.0, min_margin=1.15, max_margin=1.60)
        self.stock = 20
        self.negotiation_rounds = {}

    def send_message(self, receiver: str, performative: str, content: dict, conv_id: str):
        msg = {
            "sender": self.agent_id,
            "receiver": receiver,
            "conversation_id": conv_id,
            "performative": performative,
            "content": content
        }
        self.kernel.route_message(msg)

    def on_receive(self, message: dict, round_progress: float):
        performative = message["performative"]
        sender = message["sender"]
        conv_id = message.get("conversation_id", "default_conv")
        content = message.get("content", {})
        self.negotiation_rounds[conv_id] = self.negotiation_rounds.get(conv_id, 0) + 1

        print(f"   [{self.agent_id}] Reçu '{performative}' de {sender}: {content}")

        if performative == "CFP":
            opening_price = self.strategy.p_max
            qty = content.get("quantity", 1)
            print(f"   [{self.agent_id}] -> CFP reçu. Prix d'ouverture proposé : {opening_price}€/u")
            self.send_message(
                receiver=sender,
                performative="PROPOSE",
                content={"product": content.get("product"), "quantity": qty, "unit_price": opening_price},
                conv_id=conv_id
            )

        elif performative == "PROPOSE":
            offered_price = content.get("unit_price", 0.0)
            decision, counter_price = self.strategy.evaluate_buyer_offer(offered_price, round_progress)

            # Si trop de ping-pong (plus de 3 tours), on accepte si au moins au-dessus de p_min
            if self.negotiation_rounds[conv_id] >= 4 and offered_price >= self.strategy.p_min:
                decision = "ACCEPT_PROPOSAL"

            if decision == "ACCEPT_PROPOSAL":
                print(f"   [{self.agent_id}] -> ACCORD TROUVÉ ! Vente acceptée à {offered_price}€.")
                self.send_message(receiver=sender, performative="ACCEPT_PROPOSAL", content={"agreed_price": offered_price}, conv_id=conv_id)
                self.kernel.register_transaction(seller=self.agent_id, buyer=sender, unit_price=offered_price, quantity=content.get("quantity", 1))
            elif decision == "PROPOSE":
                print(f"   [{self.agent_id}] -> Contre-offre à {counter_price}€ (cible actuelle={self.strategy.compute_target_price(round_progress)}€).")
                self.send_message(receiver=sender, performative="PROPOSE", content={"unit_price": counter_price, "quantity": content.get("quantity", 1)}, conv_id=conv_id)
            else:
                print(f"   [{self.agent_id}] -> REFUS : {offered_price}€ est sous notre prix plancher ({self.strategy.p_min}€).")
                self.send_message(receiver=sender, performative="REJECT_PROPOSAL", content={"reason": "price_below_cost"}, conv_id=conv_id)


# =====================================================================
# 3. UN AGENT ACHETEUR D'UNE AUTRE EQUIPE (Agent Partenaire / Mock)
# =====================================================================
class BuyerAgent:
    """
    Simule l'agent d'une autre equipe cherchant a acheter notre produit fini.
    """
    def __init__(self, agent_id: str, kernel_bus, target_budget: float):
        self.agent_id = agent_id
        self.kernel = kernel_bus
        self.target_budget = target_budget

    def send_message(self, receiver: str, performative: str, content: dict, conv_id: str):
        msg = {
            "sender": self.agent_id,
            "receiver": receiver,
            "conversation_id": conv_id,
            "performative": performative,
            "content": content
        }
        self.kernel.route_message(msg)

    def on_receive(self, message: dict, round_progress: float):
        performative = message["performative"]
        sender = message["sender"]
        conv_id = message.get("conversation_id", "default_conv")
        content = message.get("content", {})

        print(f"   [{self.agent_id}] Reçu '{performative}' de {sender}: {content}")

        if performative == "PROPOSE":
            price = content.get("unit_price", 0.0)
            if price <= self.target_budget:
                print(f"   [{self.agent_id}] -> Prix convenable ({price}€ <= {self.target_budget}€). J'accepte !")
                self.send_message(receiver=sender, performative="ACCEPT_PROPOSAL", content={"agreed_price": price}, conv_id=conv_id)
                self.kernel.register_transaction(seller=sender, buyer=self.agent_id, unit_price=price, quantity=content.get("quantity", 1))
            else:
                counter = round((price + self.target_budget) / 2.0, 2)
                print(f"   [{self.agent_id}] -> Trop cher ! Je propose {counter}€.")
                self.send_message(receiver=sender, performative="PROPOSE", content={"unit_price": counter, "quantity": content.get("quantity", 1)}, conv_id=conv_id)
        
        elif performative == "ACCEPT_PROPOSAL":
            print(f"   [{self.agent_id}] -> Super ! Le vendeur a validé le prix.")


# =====================================================================
# 4. LE NOYAU DU PROFESSEUR (Middleware / Broker / Arbitre)
# =====================================================================
class SimulationKernel:
    def __init__(self):
        self.registry = {}
        self.round_progress = 0.0

    def register_agent(self, agent):
        self.registry[agent.agent_id] = agent
        print(f"[NOYAU] Agent inscrit : {agent.agent_id}")

    def route_message(self, message: dict):
        receiver_id = message["receiver"]
        if receiver_id in self.registry:
            self.registry[receiver_id].on_receive(message, self.round_progress)
        else:
            print(f"[NOYAU ERREUR] Destinataire inconnu : {receiver_id}")

    def register_transaction(self, seller: str, buyer: str, unit_price: float, quantity: int):
        total = round(unit_price * quantity, 2)
        print("\n" + "="*62)
        print(f"   ★ TRANSACTION VALIDÉE PAR LE NOYAU ★")
        print(f"   Vendeur  : {seller}")
        print(f"   Acheteur : {buyer}")
        print(f"   Montant  : {quantity}x à {unit_price}€/u = {total}€")
        print("="*62 + "\n")


# =====================================================================
# 5. DEMONSTRATION D'UN CYCLE COMPLET DE MARCHÉ
# =====================================================================
if __name__ == "__main__":
    print("\n" + "#"*65)
    print("  SIMULATION D'UNE NÉGOCIATION ENTRE AGENTS VIA LE NOYAU")
    print("#"*65 + "\n")

    noyau = SimulationKernel()

    notre_agent = MarketingAgent("Marketing_Equipe3", "Equipe 3", noyau)
    acheteur_partenaire = BuyerAgent("Acheteur_Equipe7", noyau, target_budget=65.0)

    noyau.register_agent(notre_agent)
    noyau.register_agent(acheteur_partenaire)

    print("\n--- CAS 1 : Négociation Réussie avec un Acheteur Réglo ---")
    noyau.round_progress = 0.3  # Milieu du premier round
    acheteur_partenaire.send_message(
        receiver="Marketing_Equipe3",
        performative="CFP",
        content={"product": "Produit_Fini_Alpha", "quantity": 1},
        conv_id="conv_deal_1"
    )

    print("\n--- CAS 2 : Acheteur Abusif proposant un prix sous le coût plancher ---")
    acheteur_radin = BuyerAgent("Acheteur_Radin_Equipe9", noyau, target_budget=40.0)
    noyau.register_agent(acheteur_radin)
    
    acheteur_radin.send_message(
        receiver="Marketing_Equipe3",
        performative="PROPOSE",
        content={"product": "Produit_Fini_Alpha", "quantity": 1, "unit_price": 35.0},
        conv_id="conv_deal_2"
    )

    print("Fin de la simulation.")
