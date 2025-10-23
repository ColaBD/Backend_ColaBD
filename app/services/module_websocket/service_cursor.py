import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CursorPosition:
    """Represents a user's cursor position."""
    
    def __init__(self, user_id: str, user_name: str, x: int, y: int, color: str):
        self.user_id = user_id
        self.user_name = user_name
        self.x = x
        self.y = y
        self.color = color
        self.timestamp = datetime.utcnow().timestamp() * 1000
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "timestamp": int(self.timestamp)
        }


class ServiceCursor:
    """Service to manage collaborative cursor positions."""
    
    # Storage: {schema_id: {user_id: CursorPosition}}
    _cursors: Dict[str, Dict[str, CursorPosition]] = {}
    
    def __init__(self):
        """Initialize cursor service."""
        pass
    
    def initialize_schema(self, schema_id: str) -> None:
        """Initialize cursor tracking for a schema."""
        if schema_id not in self._cursors:
            self._cursors[schema_id] = {}
            logger.info(f"Cursor tracking initialized for schema {schema_id}")
    
    def update_cursor(
        self, 
        user_id: str, 
        user_name: str, 
        x: int, 
        y: int, 
        color: str, 
        schema_id: str
    ) -> dict:
        """Update or create cursor position for a user."""
        self.initialize_schema(schema_id)
        
        cursor = CursorPosition(user_id, user_name, x, y, color)
        self._cursors[schema_id][user_id] = cursor
        
        logger.debug(f"Cursor updated for user {user_id} in schema {schema_id}: ({x}, {y})")
        
        return cursor.to_dict()
    
    def remove_cursor(self, user_id: str, schema_id: str) -> bool:
        """Remove cursor position for a user."""
        if schema_id not in self._cursors:
            return False
        
        if user_id in self._cursors[schema_id]:
            del self._cursors[schema_id][user_id]
            logger.info(f"Cursor removed for user {user_id} in schema {schema_id}")
            return True
        
        return False
    
    def get_schema_cursors(self, schema_id: str, exclude_user_id: Optional[str] = None) -> list[dict]:
        """Get all active cursors in a schema, optionally excluding a user."""
        if schema_id not in self._cursors:
            return []
        
        cursors = []
        for user_id, cursor in self._cursors[schema_id].items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            cursors.append(cursor.to_dict())
        
        return cursors
    
    def remove_user_all_cursors(self, user_id: str, schema_id: str) -> bool:
        """Remove all cursors for a user when they disconnect."""
        return self.remove_cursor(user_id, schema_id)
    
    def cleanup_schema(self, schema_id: str) -> None:
        """Clean up all cursors for a schema."""
        if schema_id in self._cursors:
            del self._cursors[schema_id]
            logger.info(f"Cursor service cleaned up for schema {schema_id}")
