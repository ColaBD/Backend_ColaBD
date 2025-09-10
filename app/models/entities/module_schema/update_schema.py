from typing import List, Dict, Any

class UpdateSchemaData:
    def __init__(self, schema_id: str, cells: List[Dict[str, Any]]):
        self.schema_id = schema_id
        self.cells = cells