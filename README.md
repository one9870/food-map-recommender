# 🍽️ 美食地圖推薦系統

一個基於 Streamlit 和 Google Maps API 的智慧餐廳推薦系統，幫助您找到最適合的餐廳。

## ✨ 功能特色

- 🔍 **智慧搜尋**：根據地點、餐廳類型、關鍵字搜尋餐廳
- 📍 **地圖顯示**：在 Google Maps 上標示餐廳位置
- ⭐ **評分系統**：顯示 Google 評分和推薦指數
- 🕒 **營業時間**：顯示餐廳是否營業中
- 🌍 **多語言支援**：支援中文和英文介面
- 📊 **推薦算法**：結合距離、評分、類型匹配的綜合推薦

## 🚀 快速開始

### 前置需求

- Python 3.7+
- Google Maps API 金鑰

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/one9870/food-map-recommender.git
cd food-map-recommender
```

2. **安裝依賴套件**
```bash
pip install streamlit requests
```

3. **設定 API 金鑰**
   - 在程式碼中設定您的 Google Maps API 金鑰
   - 或設定環境變數 `GOOGLE_MAPS_API_KEY`

4. **運行程式**
```bash
streamlit run food_fixed.py
```

5. **開啟瀏覽器**
   - 程式會自動開啟瀏覽器
   - 或手動前往：http://localhost:8501

## 📖 使用方式

1. **選擇語言**：在側邊欄選擇中文或英文
2. **輸入搜尋條件**：
   - 地點：例如「中山區，台北」
   - 餐廳類型：例如「火鍋、燒烤」
   - 關鍵字：例如「辣、牛肉」
3. **點擊搜尋**：查看餐廳列表和地圖
4. **查看詳細資訊**：點擊地圖上的標記查看餐廳詳情

## 🏗️ 專案結構

```
food-map-recommender/
├── food.py              # 原始版本
├── food_fixed.py        # 改進版本（推薦使用）
├── README.md           # 專案說明
└── .gitignore          # Git 忽略檔案
```

## 🔧 技術架構

- **前端框架**：Streamlit
- **地圖服務**：Google Maps API
- **地理編碼**：Google Geocoding API
- **餐廳搜尋**：Google Places API
- **距離計算**：Haversine 公式

## 📊 推薦算法

系統使用綜合評分算法：

- **距離分數**（40分）：距離越近分數越高
- **評分分數**（50分）：Google 評分轉換為 50 分制
- **類型匹配**（10分）：符合搜尋條件的餐廳類型

## ⚠️ 注意事項

- 需要有效的 Google Maps API 金鑰
- 需要網路連線
- API 有使用配額限制
- 建議在台灣地區使用

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 👨‍💻 作者

one9870

---

⭐ 如果這個專案對您有幫助，請給個 Star！ 