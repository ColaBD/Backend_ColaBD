from supabase import Client
from app.database.common.database_manager import db_manager


def get_supabase_client() -> Client:
    """
    Get Supabase client instance from database manager.
    
    Returns:
        Client: Configured Supabase client
    """
    return db_manager.get_supabase_client()


def get_supabase_table(table_name: str):
    """
    Get a specific table from Supabase.
    
    Args:
        table_name: Name of the table to access
        
    Returns:
        Supabase table instance
    """
    return db_manager.get_supabase_table(table_name)