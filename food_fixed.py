#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
餐廳地圖推薦系統
使用 Google Maps API 和 Streamlit 建立餐廳推薦應用
"""

import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from math import radians, cos, sin, asin, sqrt
from typing import Dict, List, Optional, Tuple

# 設定頁面配置
st.set_page_config(
    page_title="餐廳地圖推薦系統", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 從環境變數獲取 API Key（更安全）
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyBgqLteg8rjtDWjn5nvq414o9bnCHODJpQ")

# 語言選擇
lang = st.sidebar.selectbox("選擇語言 / Language", ["中文", "English"])

# 側邊欄設定
if lang == "中文":
    st.sidebar.header("搜尋設定")
    location = st.sidebar.text_input("地點", placeholder="例如：中山區，台北")
    category = st.sidebar.text_input("餐廳類型", placeholder="例如：火鍋、燒烤")
    keyword = st.sidebar.text_input("關鍵字", placeholder="例如：辣、牛肉")
    search_btn = st.sidebar.button("搜尋")
else:
    st.sidebar.header("Search Settings")
    location = st.sidebar.text_input("Location", placeholder="e.g. Zhongshan, Taipei")
    category = st.sidebar.text_input("Category", placeholder="e.g. Hotpot, BBQ")
    keyword = st.sidebar.text_input("Keyword", placeholder="e.g. spicy, beef")
    search_btn = st.sidebar.button("Search")

# 標題
if lang == "中文":
    st.title("🍽️ 餐廳地圖推薦系統")
else:
    st.title("🍽️ Restaurant Map Recommender")

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    使用 Haversine 公式計算兩點間距離（公里）
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球半徑（公里）
    return c * r

def get_location_coordinates(location: str) -> Optional[Tuple[float, float]]:
    """
    使用 Google Geocoding API 獲取地點座標
    """
    try:
        geo_url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "region": "tw",
            "key": API_KEY
        }
        response = requests.get(geo_url, params=params, timeout=10)
        response.raise_for_status()
        
        geo_data = response.json()
        if geo_data.get("results"):
            location_data = geo_data["results"][0]["geometry"]["location"]
            return location_data["lat"], location_data["lng"]
        else:
            st.warning("無法找到該地點的座標" if lang == "中文" else "Unable to find coordinates for this location")
            return None
    except requests.RequestException as e:
        st.error(f"地理編碼 API 錯誤: {e}" if lang == "中文" else f"Geocoding API error: {e}")
        return None
    except Exception as e:
        st.error(f"處理地理編碼時發生錯誤: {e}" if lang == "中文" else f"Error processing geocoding: {e}")
        return None

def search_restaurants(location: str, category: str, keyword: str) -> List[Dict]:
    """
    搜尋餐廳
    """
    try:
        # 建立搜尋查詢
        query_parts = [location, category, keyword]
        query = " ".join([part for part in query_parts if part.strip()])
        
        if not query.strip():
            st.error("請至少輸入地點或餐廳類型" if lang == "中文" else "Please enter at least location or category")
            return []
        
        # 呼叫 Places API
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "language": "zh-TW" if lang == "中文" else "en",
            "region": "tw",
            "key": API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            st.info("沒有找到相關餐廳" if lang == "中文" else "No restaurants found")
            return []
            
        return results
        
    except requests.RequestException as e:
        st.error(f"餐廳搜尋 API 錯誤: {e}" if lang == "中文" else f"Restaurant search API error: {e}")
        return []
    except Exception as e:
        st.error(f"搜尋餐廳時發生錯誤: {e}" if lang == "中文" else f"Error searching restaurants: {e}")
        return []

def calculate_recommendation_scores(results: List[Dict], center_lat: float, center_lng: float) -> List[Dict]:
    """
    計算推薦分數（100分制）
    """
    scored_results = []
    max_distance = 0
    
    # 計算距離
    for result in results:
        lat = result.get("geometry", {}).get("location", {}).get("lat")
        lng = result.get("geometry", {}).get("location", {}).get("lng")
        
        if lat and lng:
            dist = haversine(center_lng, center_lat, lng, lat)
            result["_distance_km"] = dist
            max_distance = max(max_distance, dist)
        else:
            result["_distance_km"] = None
    
    # 計算推薦分數（100分制）
    for result in results:
        # 距離分數（距離越近分數越高）- 40分
        if result["_distance_km"] is not None and max_distance > 0:
            distance_score = (1 - (result["_distance_km"] / max_distance)) * 40
        else:
            distance_score = 20  # 預設20分
        
        # 評分分數（Google評分轉換為50分制）
        rating = result.get("rating", 0)
        rating_score = (rating / 5) * 50  # 5星制轉換為50分
        
        # 類型匹配分數（10分）
        types = result.get("types", [])
        type_score = 0
        if category:
            for t in types:
                if category.lower() in t.lower():
                    type_score = 10
                    break
        elif keyword:
            for t in types:
                if keyword.lower() in t.lower():
                    type_score = 10
                    break
        
        # 綜合推薦分數（總分100分）
        recommend = distance_score + rating_score + type_score
        result["_recommend"] = round(recommend, 1)  # 四捨五入到小數點後1位
        scored_results.append(result)
    
    # 按推薦分數排序
    scored_results.sort(key=lambda x: x["_recommend"], reverse=True)
    return scored_results

def display_restaurant_info(restaurant: Dict):
    """
    顯示餐廳資訊
    """
    name = restaurant.get("name", "")
    address = restaurant.get("formatted_address", "")
    rating = restaurant.get("rating", "-")
    dist = restaurant.get("_distance_km", 0)
    recommend = restaurant.get("_recommend", 0)
    
    # 營業時間狀態
    opening_hours = restaurant.get("opening_hours", {}).get("open_now")
    if opening_hours is True:
        open_str = "營業中" if lang == "中文" else "Open"
    elif opening_hours is False:
        open_str = "已關閉" if lang == "中文" else "Closed"
    else:
        open_str = "-"
    
    # 顯示資訊
    if lang == "中文":
        st.write(f"**{name}**")
        st.write(f"📍 {address}")
        st.write(f"⭐ 評分: {rating} | 📏 距離: {dist:.2f}km | 🎯 推薦分數: {int(recommend)}分 | 🕒 {open_str}")
    else:
        st.write(f"**{name}**")
        st.write(f"📍 {address}")
        st.write(f"⭐ Rating: {rating} | 📏 Distance: {dist:.2f}km | 🎯 Score: {int(recommend)}/100 | 🕒 {open_str}")
    
    st.divider()

def create_map_html(results: List[Dict], center_lat: float, center_lng: float) -> str:
    """
    建立地圖 HTML
    """
    markers = []
    for result in results:
        lat = result.get("geometry", {}).get("location", {}).get("lat")
        lng = result.get("geometry", {}).get("location", {}).get("lng")
        name = result.get("name", "")
        address = result.get("formatted_address", "")
        rating = result.get("rating", "-")
        recommend = result.get("_recommend", 0)
        
        opening_hours = result.get("opening_hours", {}).get("open_now")
        if opening_hours is True:
            open_str = "營業中" if lang == "中文" else "Open"
        elif opening_hours is False:
            open_str = "已關閉" if lang == "中文" else "Closed"
        else:
            open_str = "-"
        
        if lat and lng:
            if lang == "中文":
                info = f"<b>{name}</b><br>{address}<br>⭐ 評分: {rating}<br>🎯 推薦分數: {int(recommend)}分<br>🕒 {open_str}"
            else:
                info = f"<b>{name}</b><br>{address}<br>⭐ Rating: {rating}<br>🎯 Score: {int(recommend)}/100<br>🕒 {open_str}"
            
            markers.append({"lat": lat, "lng": lng, "info": info})
    
    # 建立地圖 HTML
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
    return map_html

# 主要程式邏輯
col1, col2 = st.columns([1, 2])
results = []
search_center = None

with col1:
    if lang == "中文":
        st.subheader("🏪 餐廳列表")
    else:
        st.subheader("🏪 Restaurant List")
    
    if search_btn:
        # 獲取搜尋中心點座標
        if location:
            coords = get_location_coordinates(location)
            if coords:
                center_lat, center_lng = coords
                search_center = {"lat": center_lat, "lng": center_lng}
            else:
                # 使用預設座標（台北101大樓）
                center_lat, center_lng = 25.0330, 121.5654
                search_center = {"lat": center_lat, "lng": center_lng}
        else:
            # 使用預設座標（台北101大樓）
            center_lat, center_lng = 25.0330, 121.5654
            search_center = {"lat": center_lat, "lng": center_lng}
        
        # 搜尋餐廳
        results = search_restaurants(location, category, keyword)
        
        if results:
            # 計算推薦分數
            scored_results = calculate_recommendation_scores(results, center_lat, center_lng)
            
            # 顯示餐廳列表
            for restaurant in scored_results:
                display_restaurant_info(restaurant)
            
            results = scored_results
    else:
        if lang == "中文":
            st.info("搜尋結果將顯示在這裡")
        else:
            st.info("Search results will be shown here")

with col2:
    if lang == "中文":
        st.subheader("🗺️ 地圖顯示")
    else:
        st.subheader("🗺️ Map Display")
    
    if search_btn and results:
        # 建立地圖
        map_html = create_map_html(results, search_center["lat"], search_center["lng"])
        components.html(map_html, height=520)
    else:
        # 顯示預設地圖（台北101大樓）
        default_lat, default_lng = 25.0330, 121.5654
        default_map_html = f'''
        <div id="map" style="width:100%;height:500px;"></div>
        <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
        <script>
        var map = new google.maps.Map(document.getElementById('map'), {{
            center: {{lat: {default_lat}, lng: {default_lng}}},
            zoom: 15
        }});
        var marker = new google.maps.Marker({{
            position: {{lat: {default_lat}, lng: {default_lng}}},
            map: map,
            title: "台北101大樓 / Taipei 101"
        }});
        var infowindow = new google.maps.InfoWindow({{
            content: "<b>台北101大樓 / Taipei 101</b><br>預設起始點 / Default starting point"
        }});
        marker.addListener('click', function() {{
            infowindow.open(map, marker);
        }});
        </script>
        '''
        components.html(default_map_html, height=520)

# 頁腳資訊
st.markdown("---")
if lang == "中文":
    st.markdown("💡 **使用提示**: 輸入地點、餐廳類型或關鍵字來搜尋附近的餐廳")
else:
    st.markdown("💡 **Usage Tips**: Enter location, restaurant category, or keywords to search for nearby restaurants")
