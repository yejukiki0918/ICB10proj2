"""
이 스크립트는 Parquet 파일의 메타데이터를 추출하여 텍스트 형식으로 출력합니다.
"""
import pyarrow.parquet as pq

def main():
    file_path = "seoul-pops/data/LOCAL_PEOPLE_DONG_202606_tidy.parquet"
    print("Reading parquet metadata...")
    meta = pq.read_metadata(file_path)
    
    # 텍스트로 메타데이터 포맷팅
    output = []
    output.append(f"Format Version: {meta.format_version}")
    output.append(f"Creator: {meta.created_by}")
    output.append(f"Number of Rows: {meta.num_rows}")
    output.append(f"Number of Row Groups: {meta.num_row_groups}")
    output.append(f"Number of Columns: {meta.num_columns}")
    output.append(f"Serialized Size: {meta.serialized_size} bytes")
    output.append("\n[Schema]")
    output.append(str(meta.schema))
    
    output.append("\n[Row Group 0 Info]")
    rg = meta.row_group(0)
    output.append(f"  Num Rows: {rg.num_rows}")
    output.append(f"  Total Byte Size: {rg.total_byte_size}")
    
    output_str = "\n".join(output)
    print("Metadata Output:")
    print(output_str)
    
    # 보고서에 추가
    report_file = "seoul-pops/report/drop_report.md"
    with open(report_file, "a", encoding="utf-8") as f:
        f.write("\n\n## Parquet 파일 메타 정보\n```text\n")
        f.write(output_str)
        f.write("\n```\n")

if __name__ == "__main__":
    main()
