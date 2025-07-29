import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from schemas import QueryRequest, QueryResponse
from db import get_db_conn
from typing import List

app = FastAPI(
    title="CRM Data Query API",
    version="1.0.0",
    description="API for querying Microsoft Fabric CRM pipeline data. Used by GPT Action."
)

@app.get("/")
def read_root():
    return {"message": "Hello from Render!"}

ALLOWED_TABLES = {
    "leads": ["LeadID", "LeadName", "Status", "CreatedDate", "Owner"],
    "opportunities": ["OpportunityID", "Name", "Stage", "Status", "EstimatedValue", "EstimatedCloseDate", "Owner", "LastModifiedDate"],
    "opportunity_products": ["OpportunityProductID", "OpportunityID", "ProductName", "Quantity", "LineItemAmount"]
}

API_KEY = os.getenv("API_KEY")
def check_api_key(request: Request):
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/query", response_model=QueryResponse)
async def query_data(
    body: QueryRequest,
    _: None = Depends(check_api_key)
):
    # Table security
    if body.table not in ALLOWED_TABLES:
        raise HTTPException(400, detail="Unknown or forbidden table")
    for field in body.fields:
        if field not in ALLOWED_TABLES[body.table]:
            raise HTTPException(400, detail=f"Field {field} not allowed for table {body.table}")
    # Build query
    sql = f"SELECT {', '.join(body.fields)} FROM {body.table}"
    filters = []
    params = []
    if body.filters:
        for k, v in body.filters.items():
            if k not in ALLOWED_TABLES[body.table]:
                continue
            filters.append(f"{k} = ?")
            params.append(v)
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    if body.group_by:
        for gb in body.group_by:
            if gb not in ALLOWED_TABLES[body.table]:
                continue
        sql += " GROUP BY " + ", ".join(body.group_by)
    if body.limit:
        sql = sql.replace("SELECT", f"SELECT TOP {body.limit}", 1)
    # Execute
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    return QueryResponse(
        rows=rows, row_count=len(rows), fields=body.fields,
        filter_used=body.filters, group_by=body.group_by
    )
