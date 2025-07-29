import os
import pyodbc
import msal

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DB = os.getenv("SQL_DB")

def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://database.windows.net/.default"])
    if "access_token" not in result:
        raise Exception("Failed to get access token for DB")
    return result["access_token"]

def get_db_conn():
    token = get_access_token()
    # Convert token for ODBC driver
    import struct
    token_bytes = token.encode('utf-16-le')
    exptoken = struct.pack(f'<i{len(token_bytes)}s', len(token_bytes), token_bytes)
    conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={SQL_SERVER};Database={SQL_DB};Encrypt=yes;TrustServerCertificate=no;"
    conn = pyodbc.connect(conn_str, attrs_before={1256: exptoken})
    return conn
