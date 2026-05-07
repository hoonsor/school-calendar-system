# 📅 學校行事曆整合系統 (School Calendar System)

一個整合學校行事曆、放假通知、LINE Bot 和多平台行事曆同步的系統。

## 🌟 功能特色

- 🔄 **自動同步** - 從政府開放資料平台自動抓取行事曆
- 📱 **多平台支援** - 支援 Google Calendar、Apple Calendar、Outlook
- 💬 **LINE 通知** - 透過 LINE Bot 發送放假提醒
- 📄 **ICS 格式** - 產生標準 iCalendar 格式檔案
- 🔔 **即時更新** - 行事曆變動即時通知

## 📁 專案結構

```
school-calendar-system/
├── app.py                     # Flask 主應用程式
├── vercel.json                # Vercel 部署設定
├── requirements.txt           # Python 依賴
├── README.md                  # 本檔案
├── scraper/                   # 爬蟲模組
│   └── school_calendar_scraper.py
├── icalendar_generator/       # ICS 生成器
│   └── calendar_generator.py
├── line_notifier/            # LINE Bot 通知
│   └── line_notifier.py
├── frontend/                 # 前端頁面
│   └── index.html
└── data/                     # 資料儲存 (gitignore)
    └── sample_calendar.ics
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
# LINE Bot 設定
export LINE_CHANNEL_ACCESS_TOKEN="你的LINE Channel Access Token"
export LINE_CHANNEL_SECRET="你的LINE Channel Secret"
```

### 3. 執行應用程式

```bash
python app.py
```

或在 Vercel 上部署。

## 📡 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 前端頁面 |
| `/api/calendar` | GET | 取得所有行事曆事件 (JSON) |
| `/api/holidays?year=2025` | GET | 取得特定年份假期 |
| `/calendar/school.ics` | GET | 取得 ICS 格式行事曆 |
| `/health` | GET | 健康檢查 |

## 📱 加入行事曆

### Google Calendar
1. 開啟 Google Calendar
2. 其他日曆 → 從 URL 新增
3. 貼上 Calendar ID

### Apple Calendar / iCal
直接訂閱 ICS URL:
```
https://your-app.vercel.app/calendar/school.ics
```

## 💬 LINE Bot 訊息

- 傳送「訂閱」- 訂閱行事曆通知
- 傳送「幫助」- 查看使用說明
- 傳送「本週」- 查看本週行事

## 🔧 開發

### 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行
python app.py

# 測試 LINE Webhook
ngrok http 5000
```

### 部署到 Vercel

```bash
vercel
```

## 📄 授權

MIT License

## 👤 作者

hoonsoropenclaw