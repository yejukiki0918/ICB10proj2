import pandas as pd
import json

df = pd.read_csv('saramin/data/marketing_project/marketing_jobs.csv')
sample_json = json.loads(df['json_data'].iloc[0])
print(json.dumps(sample_json, indent=2, ensure_ascii=False))
