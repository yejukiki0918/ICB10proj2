import pandas as pd
import json

df = pd.read_csv('saramin/data/marketing_project/marketing_jobs.csv')
print("Columns:", df.columns.tolist())
print("Data types:\n", df.dtypes)
print("Head:\n", df.head(3))
