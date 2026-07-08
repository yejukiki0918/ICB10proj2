# 데이터 처리 리포트

## 상위 5개 행 (Tidy Data)
|    |    기준일ID |   시간대구분 |    행정동코드 |   총생활인구수 |      인구수 | 성별   | 연령대    |
|---:|---------:|--------:|---------:|---------:|---------:|:-----|:-------|
|  0 | 20260601 |       0 | 11740685 |  61126.7 | 1772.23  | 남자   | 0세부터9세 |
|  1 | 20260601 |       0 | 11740700 |  26768   | 1327.31  | 남자   | 0세부터9세 |
|  2 | 20260601 |       0 | 11110515 |  14634.2 |  493.267 | 남자   | 0세부터9세 |
|  3 | 20260601 |       0 | 11110530 |  10059.7 |  252.529 | 남자   | 0세부터9세 |
|  4 | 20260601 |       0 | 11740690 |  35192.5 | 1916.38  | 남자   | 0세부터9세 |

## 원본 데이터 정보 (info())
```
<class 'pandas.DataFrame'>
RangeIndex: 305280 entries, 0 to 305279
Data columns (total 32 columns):
 #   Column           Non-Null Count   Dtype  
---  ------           --------------   -----  
 0   기준일ID            305280 non-null  int64  
 1   시간대구분            305280 non-null  int64  
 2   행정동코드            305280 non-null  int64  
 3   총생활인구수           305280 non-null  float64
 4   남자0세부터9세생활인구수    305280 non-null  float64
 5   남자10세부터14세생활인구수  305280 non-null  float64
 6   남자15세부터19세생활인구수  305280 non-null  float64
 7   남자20세부터24세생활인구수  305280 non-null  float64
 8   남자25세부터29세생활인구수  305280 non-null  float64
 9   남자30세부터34세생활인구수  305280 non-null  float64
 10  남자35세부터39세생활인구수  305280 non-null  float64
 11  남자40세부터44세생활인구수  305280 non-null  float64
 12  남자45세부터49세생활인구수  305280 non-null  float64
 13  남자50세부터54세생활인구수  305280 non-null  float64
 14  남자55세부터59세생활인구수  305280 non-null  float64
 15  남자60세부터64세생활인구수  305280 non-null  float64
 16  남자65세부터69세생활인구수  305280 non-null  float64
 17  남자70세이상생활인구수     305280 non-null  float64
 18  여자0세부터9세생활인구수    305280 non-null  float64
 19  여자10세부터14세생활인구수  305280 non-null  float64
 20  여자15세부터19세생활인구수  305280 non-null  float64
 21  여자20세부터24세생활인구수  305280 non-null  float64
 22  여자25세부터29세생활인구수  305280 non-null  float64
 23  여자30세부터34세생활인구수  305280 non-null  float64
 24  여자35세부터39세생활인구수  305280 non-null  float64
 25  여자40세부터44세생활인구수  305280 non-null  float64
 26  여자45세부터49세생활인구수  305280 non-null  float64
 27  여자50세부터54세생활인구수  305280 non-null  float64
 28  여자55세부터59세생활인구수  305280 non-null  float64
 29  여자60세부터64세생활인구수  305280 non-null  float64
 30  여자65세부터69세생활인구수  305280 non-null  float64
 31  여자70세이상생활인구수     305280 non-null  float64
dtypes: float64(29), int64(3)
memory usage: 74.5 MB

```

## 처리 및 압축 후 데이터 정보 (info())
```
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 7 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   int32   
 1   시간대구분   int8    
 2   행정동코드   int32   
 3   총생활인구수  float64 
 4   인구수     float64 
 5   성별      category
 6   연령대     category
dtypes: category(2), float64(2), int32(2), int8(1)
memory usage: 220.1 MB

```
