from pymongo import MongoClient
from api.utils import settings
from pymongo.mongo_client import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient


def create_nosql_db():
    
    client = MongoClient(settings.MONGO_URI)

    try:
        client.admin.command("ping")
        print("MongoDB Connection Established...")
    except Exception as e:
        print(e)

    
client = MongoClient(settings.MONGO_URI)
db = client.get_database(settings.MONGO_DB_NAME)
