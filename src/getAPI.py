import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

import uuid
from supabase import create_client
from datetime import datetime

class ApiToMongo:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("mongo_uri")
        self.db_name = os.getenv("BASE_MONDOB")
        self.col_name = os.getenv("collection_mongodb")
        self.api_url = os.getenv("api_url")

        self.supabase_uri = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not all([self.uri, self.db_name, self.col_name, self.api_url]):
            raise ValueError("Missing .env vars: mongo_uri, BASE_MONDOB, collection_mongodb, api_url")

    @staticmethod
    def _extract_records(payload: Any) -> List[Dict[str, Any]]:
        """
        Essaie d'extraire une liste de documents depuis différents formats d'API:
        - payload = {"data": {"stations": [...]}}
        - payload = {"stations": [...]}
        - payload = [...]
        - payload = {"records": [...]}
        """
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]

        if isinstance(payload, dict):
            # essais fréquents
            candidates = [
                payload.get("data", {}).get("stations") if isinstance(payload.get("data"), dict) else None,
                payload.get("stations"),
                payload.get("results"),
                payload.get("data"),
            ]
            for c in candidates:
                if isinstance(c, list):
                    return [x for x in c if isinstance(x, dict)]

        # rien trouvé -> 0 records
        return []

    @staticmethod
    def _make_key() -> str:
        """Définit une clé unique pour faire un upsert propre."""
        return str(uuid.uuid1())

    def run(self) -> None:
        t0 = time.time()

        # 1) Fetch API
        r = requests.get(self.api_url, timeout=10)
        r.raise_for_status()
        payload = r.json()

        # 2) Extract records
        records = self._extract_records(payload)
        if not records:
            print("⚠️ No records found in API response (format inattendu).")
            return

        # 3) MongoDB : Connect + bulk upsert
        client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
        try:
            client.admin.command("ping")
            col = client[self.db_name][self.col_name]

            ops = []
            for doc in records:
                key = self._make_key()
                ops.append(
                    UpdateOne(
                        {"_id": key},                 # on force un id stable
                        {"$set": {"raw": doc}},       # on stocke brut au début
                        upsert=True
                    )
                )

            result = col.bulk_write(ops, ordered=False)

            dt = time.time() - t0
            print(
                "✅ Sync done | "
                f"fetched={len(records)} | "
                f"upserted={result.upserted_count} | "
                f"modified={result.modified_count} | "
                f"time={dt:.2f}s"
            )

        finally:
            client.close()

        # 4) Supabase : Connect + upsert

        supabase = create_client(self.supabase_uri, self.supabase_key)
        try:
            for doc in records:

                # --- 1. Insert or fetch site ---
                site_resp = supabase.table("sites").select("id").eq(
                    "identifiant", doc["id"]
                ).execute()

                if site_resp.data:
                    site_id = site_resp.data[0]["id"]
                else:
                    site_insert = supabase.table("sites").insert({
                        "identifiant": doc["id"],
                        "nom": doc["name"],
                        "date_installation": doc["installation_date"],
                        "longitude": doc["coordinates"]["lon"],
                        "latitude": doc["coordinates"]["lat"],
                    }).execute()
                    site_id = site_insert.data[0]["id"]

                # --- 2. Insert or fetch compteur ---
                compteur_resp = supabase.table("compteurs").select("id").eq(
                    "identifiant", doc["id_compteur"]
                ).execute()

                if compteur_resp.data:
                    compteur_id = compteur_resp.data[0]["id"]
                else:
                    compteur_insert = supabase.table("compteurs").insert({
                        "identifiant": doc["id_compteur"],
                        "nom": doc["nom_compteur"],
                        "site_id": site_id,
                    }).execute()
                    compteur_id = compteur_insert.data[0]["id"]

                # --- 3. Insert comptage ---
                supabase.table("comptages").insert({
                    "date": doc["date"],
                    "comptage_horaire": doc["sum_counts"],
                    "photos": doc["photos"],
                    "compteur_id": compteur_id,
                }).execute()

                print("Data successfully inserted")

        except:
            print("Erreur avec Supabase")



if __name__ == "__main__":
    ApiToMongo().run()