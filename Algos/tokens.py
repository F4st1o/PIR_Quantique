# tokens.py
# -------------------
# Gestion centralisée de plusieurs jetons IBM Quantum
# Chaque entrée associe un nom de personne à son token API

TOKENS = [
    {"name": "Momo",  "token": "92ab7286207cc67fad39be53074e2856360e37427bfbc7af66151d18fde505a5265c0d159ee76ecefd78c7dd79cfda5464446d47f99cdb65b80effd5cf90526b"},
    {"name": "Baptiste",    "token": "5beaf0819b6a2df9aa41c94a0e65b3d8520c89c158823545dcb70710b4ecb6efd5d524de45d2b58a1172d3675407c53edad235f46d861cec36b24bba12671853"},
    {"name": "Chloe",  "token": "your_token_for_Chloe_here"},     
    {"name": "Guillhem",  "token": "your_token_for_Guillhem_here"},   
    {"name": "Nathan",  "token": "your_token_for_Nathan_here"},     
  


    # Ajoutez autant de dictionnaires que de tokens nécessaires
]

# Fonction utilitaire pour récupérer un token par nom

def get_token_for(name: str) -> str:
    """
    Retourne le token associé au nom fourni.
    Lève une KeyError si le nom n'est pas trouvé.
    """
    for entry in TOKENS:
        if entry["name"].lower() == name.lower():
            return entry["token"]
    raise KeyError(f"Aucun token trouvé pour '{name}'")
