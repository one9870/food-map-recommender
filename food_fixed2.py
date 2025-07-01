import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
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
    hide_closed = st.sidebar.checkbox("不顯示未營業店家")
    sort_option = st.sidebar.selectbox("排序方式", ["推薦指數", "距離", "評分"])
    
    # 獲取目前位置按鈕
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 目前位置")
    get_location_btn = st.sidebar.button("獲取目前位置")
    
    search_btn = st.sidebar.button("搜尋")
else:
    st.sidebar.header("Search")
    location = st.sidebar.text_input("Location", placeholder="e.g. Zhongshan, Taipei")
    category = st.sidebar.text_input("Category", placeholder="e.g. Hotpot, BBQ")
    keyword = st.sidebar.text_input("Keyword", placeholder="e.g. spicy, beef")
    hide_closed = st.sidebar.checkbox("Hide closed restaurants")
    sort_option = st.sidebar.selectbox("Sort by", ["Recommendation", "Distance", "Rating"])
    
    # 獲取目前位置按鈕
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Current Location")
    get_location_btn = st.sidebar.button("Get Current Location")
    
    search_btn = st.sidebar.button("Search")

# 獲取使用者位置
user_location = None
if get_location_btn:
    try:
        loc = get_geolocation()
        if loc:
            user_location = {
                "lat": loc["coords"]["latitude"],
                "lng": loc["coords"]["longitude"]
            }
            if lang == "中文":
                st.sidebar.success(f"📍 已獲取位置：\n緯度：{user_location['lat']:.6f}\n經度：{user_location['lng']:.6f}")
            else:
                st.sidebar.success(f"📍 Location obtained:\nLat: {user_location['lat']:.6f}\nLng: {user_location['lng']:.6f}")
        else:
            if lang == "中文":
                st.sidebar.error("無法獲取位置，請檢查瀏覽器權限設定")
            else:
                st.sidebar.error("Unable to get location. Please check browser permissions.")
    except Exception as e:
        if lang == "中文":
            st.sidebar.error(f"獲取位置時發生錯誤：{str(e)}")
        else:
            st.sidebar.error(f"Error getting location: {str(e)}")

# 將使用者位置存儲在 session state 中
if user_location:
    st.session_state.user_location = user_location

# 檢查 session state 中是否有使用者位置
if 'user_location' not in st.session_state:
    st.session_state.user_location = None

if lang == "中文":
    st.title("🍽️ 美食地圖推薦系統")
else:
    st.title("🍽️ Restaurant Map Recommender")

@st.cache_data
def get_place_details(place_id, lang, api_key):
    """使用 place_id 獲取地點詳細資訊"""
    fields = "formatted_phone_number,opening_hours"
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&language={'zh-TW' if lang=='中文' else 'en'}&key={api_key}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json().get("result", {})
    return {}

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
            scored_results = []
            max_distance = 0
            
            # 確定計算距離的基準點
            if st.session_state.user_location:
                # 如果有使用者位置，使用使用者位置作為基準
                distance_center_lat = st.session_state.user_location["lat"]
                distance_center_lng = st.session_state.user_location["lng"]
                distance_source = "您的位置" if lang == "中文" else "Your Location"
            else:
                # 如果沒有使用者位置，使用搜尋地點作為基準
                distance_center_lat = center_lat
                distance_center_lng = center_lng
                distance_source = location if location else "搜尋中心" if lang == "中文" else "Search Center"
            
            for r in results:
                lat = r.get("geometry", {}).get("location", {}).get("lat")
                lng = r.get("geometry", {}).get("location", {}).get("lng")
                if lat and lng:
                    # 使用確定的基準點計算距離
                    dist = haversine(distance_center_lng, distance_center_lat, lng, lat)
                    r["_distance_km"] = dist
                    r["_distance_source"] = distance_source
                    max_distance = max(max_distance, dist)
                else:
                    r["_distance_km"] = None
                    r["_distance_source"] = distance_source
            
            for r in results:
                if r["_distance_km"] is not None and max_distance > 0:
                    distance_score = 1 - (r["_distance_km"] / max_distance)
                else:
                    distance_score = 0.5
                rating_score = float(r.get("rating", 0)) / 5
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
                recommend = distance_score * 0.4 + rating_score * 0.5 + type_score * 0.1
                r["_recommend"] = recommend
                scored_results.append(r)
            # 過濾未營業店家
            if hide_closed:
                scored_results = [r for r in scored_results if r.get("opening_hours", {}).get("open_now")]
            # 排序
            if (lang == "中文" and sort_option == "距離") or (lang == "English" and sort_option == "Distance"):
                scored_results.sort(key=lambda x: x.get("_distance_km", 9999))
            elif (lang == "中文" and sort_option == "評分") or (lang == "English" and sort_option == "Rating"):
                scored_results.sort(key=lambda x: float(x.get("rating", 0)), reverse=True)
            else:
                scored_results.sort(key=lambda x: x["_recommend"], reverse=True)

            # 獲取詳細資訊
            for r in scored_results:
                place_id = r.get("place_id")
                if place_id:
                    details = get_place_details(place_id, lang, API_KEY)
                    r["details"] = details
                else:
                    r["details"] = {}

            for r in scored_results:
                name = r.get("name", "")
                address = r.get("formatted_address", "")
                rating = r.get("rating", "-")
                dist = r.get("_distance_km", 0)
                distance_source = r.get("_distance_source", "")
                recommend = r.get("_recommend", 0)
                recommend_percent = int(recommend * 100)
                opening_hours = r.get("opening_hours", {}).get("open_now")
                open_str = "營業中" if opening_hours else "休息中" if opening_hours is not None else "-"
                open_str_en = "Open" if opening_hours else "Closed" if opening_hours is not None else "-"

                details = r.get("details", {})
                phone = details.get("formatted_phone_number", "未提供" if lang == "中文" else "Not available")
                hours_list = details.get("opening_hours", {}).get("weekday_text", ["未提供" if lang == "中文" else "Not available"])

                if lang == "中文":
                    with st.expander(f"{name}", expanded=False):
                        st.write(f"**{address}**")
                        st.write(f"Google評分：⭐ {rating} ｜ 距離（{distance_source}）：{dist:.2f}km ｜ 推薦指數：{recommend_percent}/100 ｜ {open_str}")
                        st.write(f"📞 電話: {phone}")
                        st.write("🕒 營業時間:")
                        for line in hours_list:
                            st.text(line)
                else:
                    with st.expander(f"{name}", expanded=False):
                        st.write(f"**{address}**")
                        st.write(f"⭐ {rating} ｜ Distance from {distance_source}: {dist:.2f}km ｜ Score: {recommend_percent}/100 ｜ {open_str_en}")
                        st.write(f"📞 Phone: {phone}")
                        st.write("🕒 Opening Hours:")
                        for line in hours_list:
                            st.text(line)
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
        lat_sum, lng_sum, count = 0, 0, 0
        for r in results:
            lat = r.get("geometry", {}).get("location", {}).get("lat")
            lng = r.get("geometry", {}).get("location", {}).get("lng")
            name = r.get("name", "")
            address = r.get("formatted_address", "")
            rating = r.get("rating", "-")
            recommend = r.get("_recommend", 0)
            recommend_percent = int(recommend * 100)
            opening_hours = r.get("opening_hours", {}).get("open_now")
            open_str = "營業中" if opening_hours else "休息中" if opening_hours is not None else "-"
            open_str_en = "Open" if opening_hours else "Closed" if opening_hours is not None else "-"
            if lat and lng:
                lat_sum += lat
                lng_sum += lng
                count += 1
                details = r.get("details", {})
                phone = details.get("formatted_phone_number", "未提供" if lang == "中文" else "Not available")
                hours_list = details.get("opening_hours", {}).get("weekday_text", [])
                hours_str = "<br>".join(hours_list) if hours_list else ("未提供" if lang == "中文" else "Not available")
                
                # 獲取距離資訊
                dist = r.get("_distance_km", 0)
                distance_source = r.get("_distance_source", "")
                
                if lang=="中文":
                    info = f"<b>{name}</b><br>{address}<br>Google評分：⭐ {rating} | 距離（{distance_source}）：{dist:.2f}km | 推薦指數: {recommend_percent}/100 | {open_str}<br>📞 {phone}<br>🕒 營業時間:<br>{hours_str}"
                else:
                    info = f"<b>{name}</b><br>{address}<br>⭐ {rating} | Distance from {distance_source}: {dist:.2f}km | Score: {recommend_percent}/100 | {open_str_en}<br>📞 {phone}<br>🕒 Opening Hours:<br>{hours_str}"
                markers.append({"lat": lat, "lng": lng, "info": info})
        
        # 地圖中心點
        if count > 0:
            center_lat = lat_sum / count
            center_lng = lng_sum / count
        elif search_center:
            center_lat = search_center["lat"]
            center_lng = search_center["lng"]
        else:
            center_lat, center_lng = 25.0478, 121.5319
        
        # 添加使用者位置標記
        user_marker_js = ""
        if st.session_state.user_location:
            user_lat = st.session_state.user_location["lat"]
            user_lng = st.session_state.user_location["lng"]
            user_info = f"📍 您的位置<br>緯度: {user_lat:.6f}<br>經度: {user_lng:.6f}" if lang == "中文" else f"📍 Your Location<br>Lat: {user_lat:.6f}<br>Lng: {user_lng:.6f}"
            user_title = "您的位置" if lang == "中文" else "Your Location"
            user_marker_js = f"""
            // 使用者位置標記（藍點）
            var userMarker = new google.maps.Marker({{
                position: {{lat: {user_lat}, lng: {user_lng}}},
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: '#4285F4',
                    fillOpacity: 1,
                    strokeColor: '#FFFFFF',
                    strokeWeight: 2
                }},
                title: '{user_title}'
            }});
            
            userMarker.addListener('click', function() {{
                var userInfoWindow = new google.maps.InfoWindow({{
                    content: '{user_info}'
                }});
                userInfoWindow.open(map, userMarker);
            }});
            """
        
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
        {user_marker_js}
        </script>
        '''
        components.html(map_html, height=520)
    else:
        # 即使沒有搜尋結果，如果有使用者位置也顯示地圖
        if st.session_state.user_location:
            user_lat = st.session_state.user_location["lat"]
            user_lng = st.session_state.user_location["lng"]
            user_info = f"📍 您的位置<br>緯度: {user_lat:.6f}<br>經度: {user_lng:.6f}" if lang == "中文" else f"📍 Your Location<br>Lat: {user_lat:.6f}<br>Lng: {user_lng:.6f}"
            user_title = "您的位置" if lang == "中文" else "Your Location"
            
            map_html = f'''
            <div id="map" style="width:100%;height:500px;"></div>
            <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
            <script>
            var map = new google.maps.Map(document.getElementById('map'), {{
                center: {{lat: {user_lat}, lng: {user_lng}}},
                zoom: 15
            }});
            
            // 使用者位置標記（藍點）
            var userMarker = new google.maps.Marker({{
                position: {{lat: {user_lat}, lng: {user_lng}}},
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: '#4285F4',
                    fillOpacity: 1,
                    strokeColor: '#FFFFFF',
                    strokeWeight: 2
                }},
                title: '{user_title}'
            }});
            
            userMarker.addListener('click', function() {{
                var userInfoWindow = new google.maps.InfoWindow({{
                    content: '{user_info}'
                }});
                userInfoWindow.open(map, userMarker);
            }});
            </script>
            '''
            components.html(map_html, height=520)
        else:
            if lang == "中文":
                st.warning("地圖將顯示於此（搜尋後顯示標記）")
            else:
                st.warning("Map will be shown here (markers after search)")

# 在底部添加推荐评分方式说明
st.markdown("---")
if lang == "中文":
    st.markdown("### 📊 推薦評分方式說明")
    st.markdown("**推薦分數評分方式為：距離 40% + Google評分 50% + 類型匹配 10%**")
    st.markdown("""
    - **距離權重 (40%)**：距離越近分數越高，基於您的位置或搜尋中心點計算
    - **Google評分權重 (50%)**：Google Maps上的用戶評分，滿分5分
    - **類型匹配權重 (10%)**：餐廳類型或關鍵字與搜尋條件的匹配程度
    """)
else:
    st.markdown("### 📊 Recommendation Scoring Method")
    st.markdown("**Recommendation score calculation: Distance 40% + Google Rating 50% + Type Match 10%**")
    st.markdown("""
    - **Distance Weight (40%)**: Higher score for closer locations, calculated from your location or search center
    - **Google Rating Weight (50%)**: User ratings from Google Maps, out of 5 stars
    - **Type Match Weight (10%)**: How well restaurant type or keywords match your search criteria
    """)

