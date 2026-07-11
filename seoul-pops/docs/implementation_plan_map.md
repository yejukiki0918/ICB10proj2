# 서울 생활인구 지도 시각화 추가 계획

사용자 요청에 따라 기존 대시보드에 **Folium 기반 코로플리스 맵(Choropleth Map)** 시각화를 추가합니다. `py-streamlit` 스킬에는 `plotly`만 사용하도록 명시되어 있으나, 지도 시각화에 한하여 명시적인 사용자 요청을 반영하여 `folium` 및 `streamlit_folium`을 사용합니다.

## User Review Required

> [!IMPORTANT]
> - 폴리움 맵 렌더링은 데이터가 커질수록(특히 모든 행정동의 폴리곤을 그릴 때) 로딩 속도가 느려질 수 있습니다. Streamlit의 `st_folium` 컴포넌트를 사용하며, 지연이 발생할 수 있음을 미리 안내해 드립니다.
> - 지도 시각화를 위해 `folium`과 `streamlit-folium` 패키지를 추가로 설치했습니다.
> - 서울시 구 단위, 동 단위 GeoJSON 파일(`seoul_gu.geojson`, `seoul_dong.geojson`)을 다운로드하여 프로젝트의 `data` 폴더에 저장했습니다. 해당 파일을 활용해 지도를 그립니다.

## Proposed Changes

### [MODIFY] [dashboard.py](file:///c:/Users/다의/Desktop/icb10proj2/seoul-pops/src/dashboard.py)
기존 스크립트에 다음 기능들을 추가합니다:
- **라이브러리 추가**: `import folium`, `from streamlit_folium import st_folium`, `import json`.
- **UI 요소 추가**: 지도 탭 내부에 **시간대 선택 슬라이더(0~23시)**와 **지역 단위 선택(자치구 / 행정동)** 라디오 버튼을 추가합니다.
- **지도 탭 신설**: 메인 패널 탭에 `🗺️ 지도 시각화`를 추가합니다.
- **데이터 집계 로직**: 선택된 '기준일'과 슬라이더의 '시간대'를 기준으로 구별 또는 동별 '총 생활인구수'를 집계합니다.
- **Folium 코로플리스 렌더링**: 집계된 데이터를 바탕으로 GeoJSON과 조인(`feature.properties.name` 활용)하여 인구 밀도 맵을 렌더링하고 `st_folium`으로 띄워줍니다.

## Verification Plan

- `dashboard.py` 스크립트를 수정한 후, 백그라운드에서 다시 `streamlit` 앱을 실행하여 정상적으로 브라우저에 지도가 렌더링되는지 확인합니다.
- 시간대 슬라이더와 구/동 옵션을 조작했을 때, 인구수에 따라 지도의 색상이 올바르게 변화하는지 수동으로 검증합니다.
