import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance = None
    _mongo_client: Optional[MongoClient] = None
    _mongo_database: Optional[Database] = None
    _supabase_client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    async def initialize(self):
        await self._initialize_mongodb()
        await self._initialize_supabase()
        logger.info("Database connections initialized successfully")

    async def _initialize_mongodb(self):
        try:
            connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
            database_name = os.getenv('MONGODB_DATABASE_NAME', 'colabd')
            
            self._mongo_client = MongoClient(connection_string)
            self._mongo_database = self._mongo_client[database_name]

            logger.info(f"MongoDB connected successfully to database: {database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise e

    async def _initialize_supabase(self):
        try:
            connection_url = os.getenv('CONNECTION_POSTGRES_SUPABASE')
            secret_key = os.getenv('SECRET_KEY_POSTGRES_SUPABASE')
            
            if not connection_url or not secret_key:
                raise ValueError("Supabase connection URL and secret key must be set in environment variables")
            
            self._supabase_client = create_client(connection_url, secret_key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise e

    def get_mongo_client(self) -> MongoClient:
        if self._mongo_client is None:
            raise RuntimeError("MongoDB client not initialized. Call initialize() first.")
        return self._mongo_client

    def get_mongo_database(self) -> Database:
        if self._mongo_database is None:
            raise RuntimeError("MongoDB database not initialized. Call initialize() first.")
        return self._mongo_database

    def get_mongo_collection(self, collection_name: str) -> Collection:
        database = self.get_mongo_database()
        return database[collection_name]

    def get_supabase_client(self) -> Client:
        if self._supabase_client is None:
            raise RuntimeError("Supabase client not initialized. Call initialize() first.")
        return self._supabase_client

    def get_supabase_table(self, table_name: str):
        client = self.get_supabase_client()
        return client.table(table_name)

    async def close_connections(self):
        if self._mongo_client:
            self._mongo_client.close()
            self._mongo_client = None
            self._mongo_database = None
            logger.info("MongoDB connection closed")
        
        # Supabase client doesn't need explicit closing
        self._supabase_client = None
        logger.info("Database connections closed successfully")


# Global database manager instance
db_manager = DatabaseManager()