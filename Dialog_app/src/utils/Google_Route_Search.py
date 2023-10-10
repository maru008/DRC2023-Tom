import requests
import json

def search_route(lat1, long1, lat2, long2, api_key,mode):
    endpoint = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{lat1},{long1}",
        "destination": f"{lat2},{long2}",
        "mode": mode,  # 公共交通機関を使用
        "key": api_key,
    }

    response = requests.get(endpoint, params=params)
    directions = response.json()

    return directions
