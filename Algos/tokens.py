# tokens.py
# -------------------
# Gestion centralisée de plusieurs jetons IBM Quantum
# Chaque entrée associe un nom de personne à son token API

TOKENS = [
    {"name": "your_name",  "token": "your_token"},
    {"name": "your_name",  "token": "your_token"}, 

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
