import requests
import json

# Download Seoul Gu and Dong GeoJSON
gu_url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
dong_url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_submunicipalities_geo_simple.json"

r = requests.get(gu_url)
with open("c:/Users/다의/Desktop/icb10proj2/seoul-pops/data/seoul_gu.geojson", "w", encoding="utf-8") as f:
    f.write(r.text)

r = requests.get(dong_url)
with open("c:/Users/다의/Desktop/icb10proj2/seoul-pops/data/seoul_dong.geojson", "w", encoding="utf-8") as f:
    f.write(r.text)

print("Downloaded.")
