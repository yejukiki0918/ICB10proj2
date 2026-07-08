"""
GeoJSON 파일 구조 및 지역명 매핑 확인 스크립트.
"""
import requests
import json

def main():
    url = "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo_simple.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        with open('geojson_sample.json', 'w', encoding='utf-8') as f:
            json.dump([f['properties'] for f in data['features']], f, ensure_ascii=False, indent=2)
        print("GeoJSON properties saved to geojson_sample.json")
    else:
        print("Failed to download GeoJSON")

if __name__ == "__main__":
    main()
