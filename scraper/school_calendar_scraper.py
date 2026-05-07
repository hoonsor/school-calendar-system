"""
學校行事曆爬蟲 - 從政府開放資料平台取得學校行事曆
"""
import requests
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

# 政府資料開放平台 API
GOVERNMENT_OPEN_DATA_BASE = "https://www.data.gov.tw"

# 放假 API (ruyut/TaiwanCalendar)
HOLIDAY_API_BASE = "https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar@master/data"

# 學校行事曆爬蟲配置
class SchoolCalendarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_holiday_data(self, year: int) -> List[Dict]:
        """從政府開放資料取得年度放假資訊"""
        url = f"{HOLIDAY_API_BASE}/{year}.json"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"取得 {year} 年行事曆失敗: {e}")
            return []
    
    def get_all_holidays(self, start_year: int = 2024, end_year: int = 2026) -> Dict:
        """取得多年假期資料"""
        all_holidays = {}
        for year in range(start_year, end_year + 1):
            holidays = self.get_holiday_data(year)
            if holidays:
                all_holidays[year] = holidays
        return all_holidays
    
    def scrape_taipei_school_calendar(self, year: int) -> List[Dict]:
        """爬取臺北市學校行事曆"""
        # 臺北市政府教育局會發布各校行事曆
        # 這裡我們用放假 API 作為基礎
        return self.get_holiday_data(year)
    
    def parse_holiday_entry(self, entry: Dict) -> Dict:
        """解析單一假期項目"""
        return {
            'date': entry.get('date', ''),
            'name': entry.get('name', ''),
            'is_holiday': entry.get('isHoliday', False),
            'is_weekend': entry.get('isWeekend', False),
            'is_special_holiday': entry.get('isSpecialHoliday', False),
            'description': entry.get('description', '')
        }
    
    def save_to_json(self, data: Dict, filename: str):
        """儲存為 JSON 檔案"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已儲存: {filename}")
    
    def load_from_json(self, filename: str) -> Dict:
        """從 JSON 檔案讀取"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

def main():
    scraper = SchoolCalendarScraper()
    
    # 測試：取得 2025 年行事曆
    print("🔍 正在取得 2025 年政府行事曆...")
    holidays_2025 = scraper.get_holiday_data(2025)
    
    if holidays_2025:
        print(f"✅ 取得 {len(holidays_2025)} 筆假期資料")
        # 儲存測試
        scraper.save_to_json(holidays_2025, 'data/holidays_2025.json')
        
        # 顯示前5筆
        for h in holidays_2025[:5]:
            print(f"  - {h.get('date')}: {h.get('name')}")
    else:
        print("❌ 無法取得假期資料")

if __name__ == "__main__":
    main()