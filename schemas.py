from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class QueryRequest(BaseModel):
    table: str = Field(..., description="The name of the table to query.")
    fields: List[str] = Field(..., description="Which fields/columns to retrieve.")
    filters: Optional[Dict[str, str]] = Field(None, description="Optional equality filters, as field:value pairs.")
    group_by: Optional[List[str]] = Field(None, description="Optional list of fields to group by.")
    limit: Optional[int] = Field(20, description="Maximum rows to return, default 20.")

class QueryResponse(BaseModel):
    rows: List[Dict[str, Any]]
    row_count: int
    fields: List[str]
    filter_used: Optional[Dict[str, str]]
    group_by: Optional[List[str]]
