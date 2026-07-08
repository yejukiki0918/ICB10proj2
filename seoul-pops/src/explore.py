import pandas as pd
import zipfile

# Try reading it as csv
try:
    df = pd.read_csv("seoul-pops/data/LOCAL_PEOPLE_DONG_202606.zip", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv("seoul-pops/data/LOCAL_PEOPLE_DONG_202606.zip", encoding="cp949")

print(df.head())
print(df.columns.tolist())
