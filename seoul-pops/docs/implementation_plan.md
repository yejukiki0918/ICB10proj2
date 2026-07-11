# 서울 생활인구 데이터 기반 EDA 대시보드 구축 계획

본 문서는 `LOCAL_PEOPLE_DONG_202606_tidy.parquet` 데이터를 기반으로 전문적인 Streamlit 대시보드를 구축하기 위한 계획입니다. 850만 건의 대용량 데이터를 처리하고, 시각적 일관성과 사용자 경험을 극대화하기 위해 `py-streamlit` 스킬의 체크리스트를 준수하여 구현합니다.

## User Review Required

> [!IMPORTANT]
> - 데이터 크기가 매우 큽니다 (약 850만 건). 초기 로딩 시 Streamlit의 캐싱(`st.cache_data`)을 적극 활용하지만, 모든 원본 데이터를 UI에서 다루면 느려질 수 있습니다. 따라서 핵심 지표들은 집계(Aggregation)된 형태로 분석 및 시각화할 예정입니다. 
> - 추가 패키지(`streamlit`, `plotly`, `openpyxl`)가 환경에 없다면 `uv`를 통해 설치하겠습니다. 동의하시나요?
> - `seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet` 파일을 요청하셨으나, 디렉토리에 존재하는 `LOCAL_PEOPLE_DONG_202606_tidy.parquet` 파일을 분석에 사용합니다.

## Open Questions

> [!WARNING]
> - 행정동별 분석 시 행정동명이 필요한데, `행정동코드_매핑정보_20241218.xlsx`를 조인하여 사용하겠습니다. 특정한 행정동(예: '연남동')이나 시군구를 기본값으로 필터링해서 보여주길 원하시나요, 아니면 전체 서울 데이터를 요약해서 먼저 보여주는 것이 좋나요?
> - 현재 폴더 구조에 맞춰 대시보드 스크립트는 `seoul-pops/src/dashboard.py` 위치에 생성하는 것으로 진행하겠습니다.

## Proposed Changes

대시보드 구현을 위해 생성할 파일 목록입니다.

### Python Scripts

#### [NEW] [dashboard.py](file:///c:/Users/다의/Desktop/icb10proj2/seoul-pops/src/dashboard.py)
Streamlit 앱 구동 스크립트입니다. 다음과 같은 구성을 가집니다.
- **데이터 전처리 및 로드 모듈**: 파켓 데이터 및 행정동 엑셀 매핑 데이터를 조인하여 반환. `@st.cache_data` 적용.
- **기본 기술 통계 및 항목 분석**: 결측치 현황, 데이터 형태 요약(`df.info()` 대체).
- **KPI 대시보드**: 전체 누적 인구수, 최대 인구수 발생 시간대, 성비 등 요약 지표.
- **시각화 (Plotly 전용)**: 
  - 시간대별/일자별 인구 추이 (Line Chart)
  - 연령대 및 성별 인구 분포 (Bar Chart & Pie Chart)
  - 상위 행정동별 인구 밀집도 (Bar Chart)
- **UI 레이아웃 구성**: `st.sidebar` 필터 (일자, 구, 동) 및 메인 패널 탭 분리 적용.

## Verification Plan

### Automated/Manual Verification
- 스크립트 작성 후 `uv run streamlit run seoul-pops/src/dashboard.py`를 실행하여 대시보드 로컬 서버를 띄웁니다.
- 메모리 부하와 차트 로딩 시간을 확인하고, 850만 건 데이터가 정상적으로 캐싱 및 처리되는지 수동 검증합니다.
- 사용자가 웹 브라우저에서 대시보드 UI, 반응성, 필터 적용 시의 동작을 확인할 수 있도록 안내합니다.
