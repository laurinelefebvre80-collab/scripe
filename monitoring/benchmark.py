import psycopg2
import time

# Informations de connexion (celles de ton docker-compose.yml)
conn_params = {
    "host": "localhost",
    "port": 5432,
    "database": "perfdb",
    "user": "postgres",
    "password": "postgres"
}

def run_stress_test(query_name, sql_query):
    print(f"Lancement de : {query_name}")
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    start_time = time.time()
    for _ in range(500): # On augmente à 500 pour que le pic soit visible
        cur.execute(sql_query)
        cur.fetchall()
    
    conn.close()
    print(f"Terminé en {time.time() - start_time:.2f} secondes")

# --- TEST 1 : REQUÊTE LENTE (Sans Index) ---
#Supprime l'index s'il existe avant de tester
#run_stress_test("SANS INDEX", "SELECT * FROM ma_table WHERE nom_station LIKE '%Gare%';")

# --- TEST 2 : REQUÊTE OPTIMISÉE (Avec Index) ---
# Crée l'index : CREATE INDEX idx_station ON ma_table(nom_station);
# run_stress_test("AVEC INDEX", "SELECT * FROM ma_table WHERE nom_station LIKE '%Gare%';")