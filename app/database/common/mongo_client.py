from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.database.common.database_manager import db_manager


def get_mongo_client() -> MongoClient:
    return db_manager.get_mongo_client()


def get_database() -> Database:
    return db_manager.get_mongo_database()


def get_collection(collection_name: str) -> Collection:
    return db_manager.get_mongo_collection(collection_name)