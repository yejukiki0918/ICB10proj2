# 총생활인구수 제외 및 최적화 리포트

## 변경 후 상위 5개 행
|    |    기준일ID |   시간대구분 |    행정동코드 |      인구수 | 성별   | 연령대    |
|---:|---------:|--------:|---------:|---------:|:-----|:-------|
|  0 | 20260601 |       0 | 11740685 | 1772.23  | 남자   | 0세부터9세 |
|  1 | 20260601 |       0 | 11740700 | 1327.31  | 남자   | 0세부터9세 |
|  2 | 20260601 |       0 | 11110515 |  493.267 | 남자   | 0세부터9세 |
|  3 | 20260601 |       0 | 11110530 |  252.529 | 남자   | 0세부터9세 |
|  4 | 20260601 |       0 | 11740690 | 1916.38  | 남자   | 0세부터9세 |

## 최종 데이터 정보 (info())
```text
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 6 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   category
 1   시간대구분   int8    
 2   행정동코드   category
 3   인구수     float32 
 4   성별      category
 5   연령대     category
dtypes: category(4), float32(1), int8(1)
memory usage: 81.5 MB

```


## Parquet 파일 메타 정보
```text
Format Version: 2.6
Creator: parquet-cpp-arrow version 24.0.0
Number of Rows: 8547840
Number of Row Groups: 9
Number of Columns: 6
Serialized Size: 9906 bytes

[Schema]
<pyarrow._parquet.ParquetSchema object at 0x000001F059ACD980>
required group field_id=-1 schema {
  optional int32 field_id=-1 기준일ID;
  optional int32 field_id=-1 시간대구분 (Int(bitWidth=8, isSigned=true));
  optional int32 field_id=-1 행정동코드;
  optional float field_id=-1 인구수;
  optional binary field_id=-1 성별 (String);
  optional binary field_id=-1 연령대 (String);
}


[Row Group 0 Info]
  Num Rows: 1048576
  Total Byte Size: 5969217
```
