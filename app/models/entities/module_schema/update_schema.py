from typing import Any

class UpdateSchemaData:
    def __init__(self, schema_id: str, cells: list[dict[str, Any]]):
        self.schema_id = schema_id
        self.cells = cells