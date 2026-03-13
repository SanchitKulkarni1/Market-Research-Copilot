# utils/mongo_logger.py

import os
from pymongo import MongoClient
from datetime import datetime
import uuid

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

try:
    client = MongoClient(MONGO_URI)
    print("✅ Connected to MongoDB successfully")
    db = client["market_research_copilot"]
    runs_collection = db["agent_runs"]
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    client = None
    db = None
    runs_collection = None

def store_raw_trace(run_data: dict) -> str:
    try:
        run_id = str(uuid.uuid4())
        run_data["run_id"] = run_id
        run_data["timestamp"] = datetime.utcnow()

        if runs_collection is None:
            raise Exception("MongoDB collection not initialized")
        
        runs_collection.insert_one(run_data)
        print(f"✅ Run {run_id} stored successfully in MongoDB")
        return run_id
    except Exception as e:
        print(f"❌ Error storing run trace: {e}")
        return None