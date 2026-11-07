import pandas as pd

file_path = "data/raw/dynamic_supply_chain_logistics_dataset.csv"

df = pd.read_csv(file_path)

print("Dataset shape:", df.shape)

print("\nColumn names:")
for column in df.columns:
    print(column)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())