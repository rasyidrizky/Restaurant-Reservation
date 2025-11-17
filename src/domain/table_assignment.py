from pydantic import BaseModel

class TableAssignment(BaseModel):
    table_id: str
    capacity: int
    area: str
