import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Load environment variables
load_dotenv()

# Read database configuration
db_host = os.getenv("SQL_SERVER_HOST")
db_port = os.getenv("SQL_SERVER_PORT")
db_user = os.getenv("SQL_ADMIN_USER")
db_password = os.getenv("SQL_ADMIN_PASSWORD")

# Validate configuration
if not all([db_host, db_port, db_user, db_password]):
    raise ValueError("Missing database configuration in .env")

# Build SQL Server connection URL
connection_url = URL.create(
    "mssql+pyodbc",
    username=db_user,
    password=db_password,
    host=db_host,
    port=int(db_port),
    database="master",
    query={
        "driver": "ODBC Driver 18 for SQL Server",
        "Encrypt": "yes",
        "TrustServerCertificate": "yes",
    },
)

# Create database engine
engine = create_engine(connection_url)

# Test connection
try:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    @@VERSION AS SQL_Server_Version,
                    GETDATE() AS Server_Time,
                    DB_NAME() AS Database_Name
            """)
        )

        row = result.fetchone()

        print("Database connection successful!")
        print("Database:", row.Database_Name)
        print("Server time:", row.Server_Time)
        print("SQL Server version:", row.SQL_Server_Version)

except Exception as error:
    print("Database connection failed.")
    print("Error type:", type(error).__name__)
    print("Error:", error)

finally:
    engine.dispose()