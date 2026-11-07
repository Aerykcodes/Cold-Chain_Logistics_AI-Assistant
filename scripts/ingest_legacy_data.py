
import os
from pathlib import Path
import urllib

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Resolve project paths
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

# 2. Load environment variables
load_dotenv(project_root / ".env")

# 3. Read database configuration
db_host = os.getenv("SQL_SERVER_HOST", "localhost")
db_port = os.getenv("SQL_SERVER_PORT", "1433")
db_user = os.getenv("SQL_ADMIN_USER")
db_password = os.getenv("SQL_ADMIN_PASSWORD")

if not all([db_host, db_port, db_user, db_password]):
    raise ValueError("Missing SQL Server configuration in .env")

# 4. Load the source dataset
data_path = (
    project_root
    / "data"
    / "raw"
    / "dynamic_supply_chain_logistics_dataset.csv"
)

df = pd.read_csv(data_path)

print(f"Source dataset loaded: {len(df)} rows")

# 5. Map original columns to legacy database columns
legacy_mapping = {
    "timestamp": "TS_UTC",
    "vehicle_gps_latitude": "V_LAT",
    "vehicle_gps_longitude": "V_LON",
    "iot_temperature": "IOT_TEMP_VAL_C",
    "cargo_condition_status": "CGO_COND_CD",
    "risk_classification": "RISK_CLS_TXT",
    "delay_probability": "DELAY_PROB_DEC",
    "port_congestion_level": "PRT_CNG_LVL",
    "route_risk_level": "RT_RSK_IDX",
}

# 6. Select and rename columns
df_legacy = df[list(legacy_mapping.keys())].rename(
    columns=legacy_mapping
)

# 7. Add ingestion flag
df_legacy["SYS_INGEST_FLAG"] = "Y"

print(f"Transformed dataset: {df_legacy.shape}")

# 8. Build SQL Server connection
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={db_host},{db_port};"
    f"DATABASE=master;"
    f"UID={db_user};"
    f"PWD={db_password};"
    f"Encrypt=no;"
    f"TrustServerCertificate=yes;"
)

params = urllib.parse.quote_plus(connection_string)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}"
)

# 9. Insert records into SQL Server
table_name = "TBL_SC_FLEET_HIST_RAW"

try:
    with engine.begin() as connection:
        df_legacy.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False,
            schema="dbo",
            chunksize=1000,
        )

        result = connection.execute(
            text("SELECT COUNT(*) FROM dbo.TBL_SC_FLEET_HIST_RAW")
        )

        total_rows = result.scalar()

    print("\nLegacy data ingestion completed!")
    print(f"Rows inserted: {total_rows}")
    print(f"Target table: dbo.{table_name}")

finally:
    engine.dispose()
