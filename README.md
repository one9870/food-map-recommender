# ccClub2025春季專案計畫-食刻導航 (Gourmet Navigator)

**使用Streamlit和Google Maps API的智慧餐廳推薦系統，幫助您找到最適合的餐廳。**

---

## (一)功能特色

- 🔍 **智慧搜尋**：根據地點、餐廳類型、關鍵字搜尋餐廳
- 📍 **地圖顯示**：在 Google Maps 上標示餐廳位置
- ⭐ **評分系統**：顯示 Google 評分和推薦指數
- 🕒 **營業時間**：顯示餐廳是否營業中
- 🌍 **多語言支援**：支援中文和英文介面
- 📊 **推薦算法**：結合距離、評分、類型匹配的綜合推薦

## (二)環境需求

- Python 3.7以上版本
- 您個人的Google Maps API Key

## (三)安裝步驟

1. **複製專案**
```bash
git clone https://github.com/one9870/food-map-recommender.git
cd food-map-recommender
```

2. **安裝依賴套件**
```bash
pip install streamlit requests
```

3. **設定API 金鑰**
   - 在程式碼中設定您的 Google Maps API 金鑰
   - 或設定環境變數 `GOOGLE_MAPS_API_KEY`

4. **運行程式**
```bash
streamlit run food_fixed.py
```

5. **開啟瀏覽器**
   - 程式會自動開啟瀏覽器
   - 或手動前往：http://localhost:8501 (預設port)

## (四)使用方式

1. **選擇語言**：在側邊欄選擇中文或英文
2. **輸入搜尋條件**：
   - 地點：例如「中山區，台北」
   - 餐廳類型：例如「火鍋、燒烤」
   - 關鍵字：例如「辣、牛肉」
3. **點擊搜尋**：查看餐廳列表和地圖
4. **查看詳細資訊**：點擊地圖上的標記查看餐廳詳情

## (五)專案結構圖

```
food-map-recommender/
├── food.py              # 原始版本
├── food_fixed.py        # 修正版本
├── README.md            # 專案說明
└── .gitignore           # Git忽略檔案
```

## (六)技術架構

- **前端框架**：使用Streamlit
- **地圖服務**：串接Google Maps API
- **地理編碼**：串接Google Geocoding API
- **餐廳搜尋**：串接Google Places API
- **距離計算**：運用Haversine 公式

## (七)推薦評分計算法

使用綜合評分算法：
- **距離分數**（40分）：距離越近分數越高
- **評分分數**（50分）：將Google評分轉換為50分制
- **類型匹配**（10分）：符合搜尋條件的餐廳類型

## (八)注意事項

1. 需要有效的 Google Maps API Key
2. 需要有網路連線
3. 注意API有使用配額限制
4. 目前僅建議在台灣本島使用

## (九)授權

MIT License

## (十)作者

one9870

---

⭐ 如果這個專案對您有幫助，請給個 Star！ 

# 餐廳地圖推薦系統

一個使用 Google Maps API 和 Streamlit 建立的餐廳推薦應用程式。

## 功能特色

- 🗺️ 互動式地圖顯示
- 🔍 多條件搜尋（地點、類型、關鍵字）
- ⭐ 智能推薦評分系統
- 🌐 中英文雙語介面
- 📱 響應式設計

## 本地執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
streamlit run food_fixed.py
```

## 部署到網路

### 方法一：Streamlit Cloud（推薦）

1. 將程式碼推送到 GitHub
2. 前往 [share.streamlit.io](https://share.streamlit.io)
3. 連接 GitHub 帳號
4. 選擇您的 repository
5. 設定環境變數 `GOOGLE_MAPS_API_KEY`
6. 部署完成！

### 方法二：Heroku

1. 建立 `Procfile`：
```
web: streamlit run food_fixed.py --server.port=$PORT --server.address=0.0.0.0
```

2. 建立 `setup.sh`：
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. 在 Heroku 設定環境變數 `GOOGLE_MAPS_API_KEY`

### 方法三：Railway

1. 連接 GitHub repository
2. 設定環境變數
3. 自動部署

### 方法四：Vercel

1. 建立 `vercel.json`：
```json
{
  "builds": [
    {
      "src": "food_fixed.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "food_fixed.py"
    }
  ]
}
```

## 環境變數設定

在部署平台上設定以下環境變數：

- `GOOGLE_MAPS_API_KEY`: 您的 Google Maps API 金鑰

## 注意事項

- 確保 Google Maps API 金鑰有足夠的配額
- 建議設定 API 金鑰的網域限制
- 免費版 Streamlit Cloud 有使用限制

## 技術架構

- **前端**: Streamlit
- **地圖**: Google Maps API
- **搜尋**: Google Places API
- **語言**: Python 3.8+ 