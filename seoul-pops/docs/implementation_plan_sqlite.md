# SQLite 기반 대시보드 성능 최적화 계획

기존 대시보드의 로딩 속도와 연산 비용을 줄이기 위해, 850만 건의 원본 파켓(Parquet) 데이터를 매번 불러오고 그룹화하는 대신 **사전 집계(Pre-aggregation)**된 데이터를 SQLite DB에 저장하여 활용하는 아키텍처로 변경합니다.

## User Review Required

> [!IMPORTANT]
> - **필터링 제약 발생**: 원본 데이터를 불러와서 동적으로 다차원(일자+구+연령대+시간대) 필터링을 하던 기존 방식과 달리, 사전 집계된 뷰(View) 테이블을 사용하게 되면 *특정 연령대만 필터링한 상태에서의 지도 밀집도* 등을 계산하려면 모든 차원 조합이 필요해져 용량이 다시 커질 수 있습니다. 
> - 본 계획에서는 **가장 부하가 큰 지도 시각화(코로플리스 맵)와 KPI, 차트 데이터를 위한 특화된 집계 테이블**을 구성하겠습니다. 사이드바 필터 중 '연령대' 등의 상세 필터가 일부 차트(지도 등)에는 적용되지 않고 전체 합산 기준으로 나타날 수 있습니다. (동의하시나요?)
> - SQLite DB 파일은 `seoul-pops/data/dashboard.db`로 생성할 예정입니다.

## Proposed Changes

### 1. [NEW] [build_sqlite.py](file:///c:/Users/다의/Desktop/icb10proj2/seoul-pops/src/build_sqlite.py)
파켓 파일과 행정동 매핑 데이터를 읽어 사전 집계 후 SQLite DB로 저장하는 전처리 스크립트입니다.
- **`agg_map_gu`**: `[기준일ID, 시간대구분, 시군구명] -> 인구수 합계` (약 18,000행)
- **`agg_map_dong`**: `[기준일ID, 시간대구분, 시군구명, 행정동명] -> 인구수 합계` (약 300,000행)
- **`agg_time`**: `[기준일ID, 시간대구분] -> 인구수 합계`
- **`agg_demo`**: `[기준일ID, 성별, 연령대] -> 인구수 합계`

### 2. [MODIFY] [dashboard.py](file:///c:/Users/다의/Desktop/icb10proj2/seoul-pops/src/dashboard.py)
Streamlit 대시보드가 파켓 대신 SQLite를 참조하도록 리팩토링합니다.
- `sqlite3` 및 `pandas.read_sql`을 사용하여 필요한 테이블만 즉시 로드.
- `@st.cache_data`를 활용해 DB 쿼리 결과를 캐싱하여 로딩 및 필터링 속도 대폭 단축.
- 지도 시각화 부분은 `agg_map_gu` 및 `agg_map_dong` 테이블에서 데이터를 가져오도록 쿼리 구조 변경.

## Verification Plan

- `uv run python seoul-pops/src/build_sqlite.py`를 실행하여 `.db` 파일이 성공적으로 생성되고 파일 크기가 획기적으로 줄어드는지 확인합니다.
- 대시보드를 다시 실행하여 초기 렌더링 속도와 슬라이더 조정 시 지도 업데이트 속도가 매우 빨라졌는지 수동 검증합니다.
