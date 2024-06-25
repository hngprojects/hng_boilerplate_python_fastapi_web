from decouple import config

MONGO_URI = config("MONGO_URI")
MONGO_DB_NAME = config("MONGO_DB_NAME")