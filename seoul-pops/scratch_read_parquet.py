import pandas as pd
import json

df = pd.read_parquet(r"c:\Users\다의\Desktop\icb10proj2\seoul-pops\data\LOCAL_PEOPLE_DONG_202606_tidy.parquet")
info = {
    "columns": df.columns.tolist(),
    "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
    "shape": df.shape,
    "head": df.head(3).to_dict(orient="records")
}
print(json.dumps(info, ensure_ascii=False, indent=2))
