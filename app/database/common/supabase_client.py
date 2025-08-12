from supabase import Client
from app.database.common.database_manager import db_manager


def get_supabase_client() -> Client:
    return db_manager.get_supabase_client()


def get_supabase_table(table_name: str):
    return db_manager.get_supabase_table(table_name)