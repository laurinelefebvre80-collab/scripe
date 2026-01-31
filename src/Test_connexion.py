import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()
uri = os.getenv("mongo_uri")

def test_connection():
    try:
        # Tenter d'ouvrir une connexion
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # La commande 'ping' vérifie si le serveur répond
        client.admin.command('ping')
        print("✅ Félicitations ! La connexion à MongoDB Atlas a réussi.")
        
        # Afficher les bases de données existantes
        print("Tes bases de données :", client.list_database_names())
        
    except Exception as e:
        print("❌ Échec de la connexion.")
        print(f"L'erreur est : {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_connection()
    

