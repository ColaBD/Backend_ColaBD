from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.database.common.database_manager import db_manager


def get_mongo_client() -> MongoClient:
    """Get MongoDB client instance from database manager."""
    return db_manager.get_mongo_client()


def get_database() -> Database:
    """Get the MongoDB database instance from database manager."""
    return db_manager.get_mongo_database()


def get_collection(collection_name: str) -> Collection:
    """Get any collection by name from database manager."""
    return db_manager.get_mongo_collection(collection_name)