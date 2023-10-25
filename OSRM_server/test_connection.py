import requests

loc_pick = [141.348117, 43.069060]
loc_del = [142.449705, 44.0997897]
query_url = "http://localhost:5000/route/v1/driving/{},{};{},{}?steps=true".format(loc_pick[0], loc_pick[1], loc_del[0], loc_del[1])
response = requests.get(query_url)

result = response.json()
print("get result data")
route = result["routes"][0]
legs = route["legs"][0]["steps"]
list_locations = []
for point in legs:
    for it in point["intersections"]:
        list_locations.append(it["location"][::-1])
        
loc_mid = [(loc_pick[0]+loc_del[0])/2, (loc_pick[1]+loc_del[1])/2]

import folium
folium_map = folium.Map(location=loc_mid[::-1], zoom_start=14)
folium.Marker(location=loc_pick[::-1], icon=folium.Icon(color='red')).add_to(folium_map)
folium.Marker(location=loc_del[::-1]).add_to(folium_map)
line = folium.vector_layers.PolyLine(locations=list_locations, color='black', weight=10)
line.add_to(folium_map)
folium_map.save("map.html")