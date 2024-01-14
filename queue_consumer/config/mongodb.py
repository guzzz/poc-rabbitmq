import os

from pymongo import MongoClient


MONGO_DATABASE_URL: str = os.getenv("MONGO_DATABASE_URL")

mongoclient = MongoClient(
    MONGO_DATABASE_URL,
    uuidRepresentation='standard'
)
