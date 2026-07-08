import pandas as pd
import os

data_dir = 'c:/Users/다의/Desktop/icb10proj2/illumiel/data'
output_file = 'c:/Users/다의/Desktop/icb10proj2/illumiel/report/analysis_results.txt'

files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx') or f.endswith('.csv')]

with open(output_file, 'w', encoding='utf-8') as f:
    for file in files:
        f.write(f"\n--- {file} ---\n")
        file_path = os.path.join(data_dir, file)
        try:
            if file.endswith('.xlsx'):
                df = pd.read_excel(file_path, nrows=5)
            else:
                df = pd.read_csv(file_path, nrows=5)
            f.write("Columns: " + ", ".join(list(df.columns)) + "\n")
            f.write("First row: " + str(df.iloc[0].to_dict()) + "\n")
        except Exception as e:
            f.write(f"Error reading {file}: {e}\n")

