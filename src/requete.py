import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("mongo_uri"))
db = client[os.getenv("BASE8MONDOB")]
col = db[os.getenv("collection_mongodb")]

def lancer_requete_optimisee():
    # Requête : Chercher les stations qui ont plus de 10 vélos mécaniques disponibles
    query = {"numbikesavailable": {"$gt": 10}}
    
    # MESURE DU TEMPS (Côté Python)
    debut = time.time()
    
    resultats = col.find(query)
    
    fin = time.time()
    print(f"Nombre de stations trouvées : {col.count_documents(query)}")
    print(f"Temps de réponse Python : {fin - debut:.4f} secondes")

lancer_requete_optimisee()