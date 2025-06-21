import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from math import radians, cos, sin, asin, sqrt

# 必須最前面呼叫
st.set_page_config(page_title="美食地圖推薦系統", layout="wide")

API_KEY = "AIzaSyBgqLteg8rjtDWjn5nvq414o9bnCHODJpQ"  

# 語言切換
lang = st.sidebar.selectbox("語言 Language", ["中文", "English"])

# 側邊搜尋欄
if lang == "中文":
    st.sidebar.header("搜尋條件")
    location = st.sidebar.text_input("地區", placeholder="如：台北市中山區")
    category = st.sidebar.text_input("餐廳類型", placeholder="如：火鍋、燒烤")
    keyword = st.sidebar.text_input("關鍵字", placeholder="如：麻辣、牛肉")
    search_btn = st.sidebar.button("搜尋")
else:
    st.sidebar.header("Search")
    location = st.sidebar.text_input("Location", placeholder="e.g. Zhongshan, Taipei")
    category = st.sidebar.text_input("Category", placeholder="e.g. Hotpot, BBQ")
    keyword = st.sidebar.text_input("Keyword", placeholder="e.g. spicy, beef")
    search_btn = st.sidebar.button("Search")

if lang == "中文":
    st.title("🍽️ 美食地圖推薦系統")
else:
    st.title("🍽️ Restaurant Map Recommender")

# Haversine公式計算距離（公里）
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球半徑（公里）
    return c * r

col1, col2 = st.columns([1, 2])
results = []
map_html = None
search_center = None

with col1:
    if lang == "中文":
        st.subheader("餐廳列表")
    else:
        st.subheader("Restaurant List")
    if search_btn:
        # 1. 取得搜尋地點經緯度
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&region=tw&key={API_KEY}"
        geo_resp = requests.get(geo_url)
        geo_data = geo_resp.json()
        if geo_data.get("results"):
            search_center = geo_data["results"][0]["geometry"]["location"]
            center_lat, center_lng = search_center["lat"], search_center["lng"]
        else:
            center_lat, center_lng = 25.0478, 121.5319  # 台北車站
            search_center = {"lat": center_lat, "lng": center_lng}
        # 2. Places API 查詢
        query = f"{location} {category} {keyword}".strip()
        url = (
            f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&language={'zh-TW' if lang=='中文' else 'en'}&region=tw&key={API_KEY}"
        )
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if not results:
                st.info("查無結果" if lang=="中文" else "No results found.")
            # 3. 計算推薦指數
            scored_results = []
            max_distance = 0
            for r in results:
                lat = r.get("geometry", {}).get("location", {}).get("lat")
                lng = r.get("geometry", {}).get("location", {}).get("lng")
                if lat and lng:
                    dist = haversine(center_lng, center_lat, lng, lat)
                    r["_distance_km"] = dist
                    max_distance = max(max_distance, dist)
                else:
                    r["_distance_km"] = None
            for r in results:
                # 距離分數（越近越高）
                if r["_distance_km"] is not None and max_distance > 0:
                    distance_score = 1 - (r["_distance_km"] / max_distance)
                else:
                    distance_score = 0.5
                # 評分分數
                rating_score = float(r.get("rating", 0)) / 5
                # 類型相似度
                types = r.get("types", [])
                type_score = 0
                if category:
                    for t in types:
                        if category.lower() in t.lower():
                            type_score = 1
                            break
                elif keyword:
                    for t in types:
                        if keyword.lower() in t.lower():
                            type_score = 1
                            break
                # 推薦指數
                recommend = distance_score * 0.4 + rating_score * 0.5 + type_score * 0.1
                r["_recommend"] = recommend
                scored_results.append(r)
            # 4. 依推薦指數排序
            scored_results.sort(key=lambda x: x["_recommend"], reverse=True)
            for r in scored_results:
                name = r.get("name", "")
                address = r.get("formatted_address", "")
                rating = r.get("rating", "-")
                dist = r.get("_distance_km", 0)
                recommend = r.get("_recommend", 0)
                # 取得營業時間
                opening_hours = r.get("opening_hours", {}).get("open_now")
                open_str = "營業中" if opening_hours else "休息中" if opening_hours is not None else "-"
                if lang == "中文":
                    st.write(f"**{name}**\n{address}\n⭐ {rating} ｜ 距離：{dist:.2f}km ｜ 推薦指數：{recommend:.2f} ｜ {open_str}")
                else:
                    open_str_en = "Open" if opening_hours else "Closed" if opening_hours is not None else "-"
                    st.write(f"**{name}**\n{address}\n⭐ {rating} ｜ Distance: {dist:.2f}km ｜ Score: {recommend:.2f} ｜ {open_str_en}")
            # 傳給地圖用
            results = scored_results
        else:
            st.error("API 錯誤，請檢查金鑰或網路。" if lang=="中文" else "API error. Please check your key or network.")
    else:
        st.info("搜尋結果將顯示於此。" if lang=="中文" else "Results will be shown here.")

with col2:
    if lang == "中文":
        st.subheader("地圖顯示")
    else:
        st.subheader("Map Display")
    # 嵌入 Google Maps
    if search_btn and results:
        # 取得所有標記
        markers = []
        for r in results:
            lat = r.get("geometry", {}).get("location", {}).get("lat")
            lng = r.get("geometry", {}).get("location", {}).get("lng")
            name = r.get("name", "")
            address = r.get("formatted_address", "")
            rating = r.get("rating", "-")
            recommend = r.get("_recommend", 0)
            opening_hours = r.get("opening_hours", {}).get("open_now")
            open_str = "營業中" if opening_hours else "休息中" if opening_hours is not None else "-"
            open_str_en = "Open" if opening_hours else "Closed" if opening_hours is not None else "-"
            if lat and lng:
                info = f"<b>{name}</b><br>{address}<br>⭐ {rating}<br>推薦指數: {recommend:.2f}<br>{open_str}" if lang=="中文" else f"<b>{name}</b><br>{address}<br>⭐ {rating}<br>Score: {recommend:.2f}<br>{open_str_en}"
                markers.append({"lat": lat, "lng": lng, "info": info})
        # 地圖中心點
        if search_center:
            center_lat = search_center["lat"]
            center_lng = search_center["lng"]
        elif markers:
            center_lat = markers[0]["lat"]
            center_lng = markers[0]["lng"]
        else:
            center_lat, center_lng = 25.0478, 121.5319
        # 產生地圖 HTML
        map_html = f'''
        <div id="map" style="width:100%;height:500px;"></div>
        <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
        <script>
        var map = new google.maps.Map(document.getElementById('map'), {{
            center: {{lat: {center_lat}, lng: {center_lng}}},
            zoom: 15
        }});
        var infowindow = new google.maps.InfoWindow();
        var markers = {markers};
        markers.forEach(function(m) {{
            var marker = new google.maps.Marker({{
                position: {{lat: m.lat, lng: m.lng}},
                map: map
            }});
            marker.addListener('click', function() {{
                infowindow.setContent(m.info);
                infowindow.open(map, marker);
            }});
        }});
        </script>
        '''
        components.html(map_html, height=520)
    else:
        if lang == "中文":
            st.warning("地圖將顯示於此（搜尋後顯示標記）")
        else:
            st.warning("Map will be shown here (markers after search)")

