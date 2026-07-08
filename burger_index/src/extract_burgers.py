"""
상가(상권)정보 데이터에서 버거킹, 맥도날드, KFC, 롯데리아(영문 포함) 데이터를 추출하여 
하나의 CSV 파일(burger.csv)로 저장하는 스크립트입니다.
"""
import os
import glob
import csv

# Directory paths
data_dir = os.path.join("burger_index", "data")
output_file = os.path.join(data_dir, "burger.csv")

# Find all CSV files in the data directory (except the output file itself)
csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
csv_files = [f for f in csv_files if not f.endswith("burger.csv")]

# Target keywords
keywords = ["버거킹", "맥도날드", "kfc", "케이에프씨", "롯데리아", "burger king", "mcdonald", "lotteria"]

header_written = False

print(f"Found {len(csv_files)} files.")

with open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    writer = None
    
    for file in csv_files:
        print(f"Processing: {file}")
        # Try utf-8 first, then cp949
        try:
            encoding = 'utf-8'
            with open(file, 'r', encoding=encoding) as f_test:
                f_test.read(100)
        except UnicodeDecodeError:
            encoding = 'cp949'
            
        with open(file, 'r', encoding=encoding, newline='') as f_in:
            reader = csv.reader(f_in)
            try:
                header = next(reader)
            except StopIteration:
                continue
                
            if not header_written:
                writer = csv.writer(f_out)
                writer.writerow(header)
                header_written = True
                
            # Find the index of "상호명"
            # It might have BOM or quotes, let's match substring
            shop_name_idx = -1
            for i, col in enumerate(header):
                if "상호명" in col:
                    shop_name_idx = i
                    break
            
            if shop_name_idx == -1:
                # If not found, assume it's the second column (index 1) which is standard
                shop_name_idx = 1
                
            for row in reader:
                if len(row) > shop_name_idx:
                    shop_name = row[shop_name_idx].lower()
                    if any(kw in shop_name for kw in keywords):
                        writer.writerow(row)

print(f"Finished writing to {output_file}")
