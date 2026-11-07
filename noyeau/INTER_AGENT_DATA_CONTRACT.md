
### Registre des objets partages

Bus d'echange inter-agents — document commun a toutes les equipes

Ce document liste les types d'objets que les agents peuvent produire ou consommer via le bus d'echange du noyau (voir AGENT_INTEGRATION_CONTRACT.docx, section 6). Il concerne surtout la filiere automatisation metier, mais rien n'empeche un agent IoT ou cybersecurite de produire un objet reutilisable par un autre agent (par exemple, un capteur de stock connecte peut produire le meme objet stock_level qu'un agent logiciel classique).

Si votre agent a besoin d'un type d'objet qui n'est pas dans ce registre, ouvrez une issue sur le depot GitHub du noyau pour en proposer l'ajout plutot que de l'inventer seul : c'est ce document, partage par toutes les equipes, qui garantit que deux agents developpes separement se comprennent.

Exemple de chaine de dependances (filiere automatisation metier)

Agent Commercial --produit--> commande
                                  |
                                  v (consomme par)
Agent Stock --consomme-- commande --produit--> stock_level, mouvement_stock
                                                        |
                                                        v
Agent Logistique --consomme-- stock_level, commande --produit--> expedition
                                                                        |
                                                                        v
Agent Facturation --consomme-- commande, expedition --produit--> facture

Une entreprise peut ne souscrire qu'a certains de ces agents : l'objet manquant peut alors etre saisi manuellement par un employe depuis le tableau de bord.


### 1. commande

{
  "numero_commande": "CMD-2027-0001",
  "date_commande": "2027-01-10T10:00:00Z",
  "client": { "nom": "Societe Dupont", "email": "contact@dupont.fr" },
  "lignes": [{ "sku": "SKU-001", "quantite": 10, "prix_unitaire_ht": 4.50 }],
  "montant_total_ht": 45.00,
  "statut": "en_attente"
}

statut : en_attente, confirmee, expediee, facturee, annulee.


### 2. stock_level

{
  "sku": "SKU-001",
  "designation": "Cable HDMI 2m",
  "quantite_disponible": 42,
  "seuil_alerte": 10,
  "entrepot": "Entrepot Nord"
}

Peut etre produit par un agent logiciel de gestion de stock, ou directement par un agent IoT de pesee connectee : les deux publient le meme type d'objet.


### 3. mouvement_stock

{
  "id_mouvement": "MVT-2027-0456",
  "sku": "SKU-001",
  "type_mouvement": "sortie",
  "quantite": 10,
  "reference_commande": "CMD-2027-0001"
}

type_mouvement : entree, sortie, ajustement.


### 4. expedition

{
  "numero_expedition": "EXP-2027-0089",
  "reference_commande": "CMD-2027-0001",
  "transporteur": "Colissimo",
  "numero_suivi": "6A12345678901",
  "statut": "en_transit"
}

statut : preparation, en_transit, livree, retour.


### 5. facture

{
  "numero_facture": "FAC-2027-0033",
  "reference_commande": "CMD-2027-0001",
  "montant_total_ttc": 54.00,
  "statut_paiement": "en_attente"
}

statut_paiement : en_attente, payee, en_retard, annulee.


### 6. prospect

{
  "id_prospect": "PROS-2027-0210",
  "nom": "Martin Leroy",
  "email": "martin.leroy@example.com",
  "score_interet": 72,
  "statut": "qualifie"
}


### 7. ticket_support

{
  "id_ticket": "TCK-2027-0077",
  "sujet": "Retard de livraison",
  "reference_commande": "CMD-2027-0001",
  "priorite": "moyenne",
  "statut": "ouvert"
}


### 8. mesure_capteur (filiere IoT)

Permet a un agent IoT de partager une lecture de capteur avec un autre agent (par exemple un agent de reporting qui agrege plusieurs sources).

{
  "capteur_id": "TEMP-ENTREPOT-03",
  "type_mesure": "temperature",
  "valeur": 6.2,
  "unite": "celsius",
  "horodatage": "2027-01-10T10:00:00Z"
}


### Regles communes

L'identifiant metier (external_id) correspond au champ "numero" ou "id" naturel de l'objet.

Les dates sont au format ISO 8601, en UTC.

Un champ inconnu recu par un agent doit etre ignore silencieusement, jamais provoquer une erreur : cela permet de faire evoluer un objet sans casser les agents existants.

La suppression ou le renommage d'un champ obligatoire necessite une validation prealable par l'enseignant.


### Proposer un nouveau type d'objet

Ouvrez une issue sur le depot GitHub du noyau avec le schema propose et la liste des agents concernes. Une fois validee, la description est ajoutee a ce document et devient utilisable par toutes les equipes.
