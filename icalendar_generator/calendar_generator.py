"""
iCalendar (.ics) 生成器 - 將假期資料轉換為標準行事曆格式
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from icalendar import Calendar, Event, Timezone

# 臺灣時區
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

class CalendarGenerator:
    def __init__(self, school_name: str = "臺灣學校"):
        self.school_name = school_name
        self.calendar = Calendar()
        self.calendar.add('prodid', f'-//{self.school_name}//School Calendar//TW')
        self.calendar.add('version', '2.0')
        self.calendar.add('calscale', 'GREGORIAN')
        self.calendar.add('method', 'PUBLISH')
        
        # 加入時區資訊
        tz = Timezone()
        tz.add('tzid', 'Asia/Taipei')
        tz.add('x-lic-location', 'Asia/Taipei')
        self.calendar.add(tz)
    
    def add_holiday(self, date_str: str, name: str, description: str = '', 
                    is_full_day: bool = True) -> Event:
        """加入單一假期事件"""
        event = Event()
        event.add('summary', name)
        event.add('description', description or f'{name} - 放假一日')
        
        # 解析日期
        if len(date_str) == 8:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            start_date = Taipei_TZ.localize(datetime(year, month, day, 0, 0, 0))
            end_date = Taipei_TZ.localize(datetime(year, month, day, 23, 59, 59))
        else:
            start_date = datetime.strptime(date_str, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        
        if is_full_day:
            event.add('dtstart', start_date.strftime('%Y%m%d'))
            event.add('dtend', end_date.strftime('%Y%m%d'))
            event.add('dtstamp', start_date)
        else:
            event.add('dtstart', start_date)
            event.add('dtend', end_date)
        
        # 設定分類
        event.add('categories', ['放假', '國定假日'])
        
        # 加上 UID
        uid = f"{date_str}-{name}@school-calendar.tw"
        event.add('uid', uid)
        
        self.calendar.add(event)
        return event
    
    def add_school_event(self, date_str: str, name: str, description: str = '',
                         location: str = '', event_type: str = 'event') -> Event:
        """加入學校活動事件"""
        event = Event()
        event.add('summary', f'【{event_type}】{name}')
        event.add('description', description)
        if location:
            event.add('location', location)
        
        if len(date_str) == 8:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            start_date = Taipei_TZ.localize(datetime(year, month, day, 0, 0, 0))
        else:
            start_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        event.add('dtstart', start_date.strftime('%Y%m%d'))
        event.add('dtend', (start_date + timedelta(days=1)).strftime('%Y%m%d'))
        event.add('dtstamp', start_date)
        
        uid = f"{date_str}-{name}@school-calendar.tw"
        event.add('uid', uid)
        
        self.calendar.add(event)
        return event
    
    def add_recurring_event(self, name: str, start_date: str, end_date: str,
                            description: str = '', frequency: str = 'WEEKLY',
                            until: str = '20260630') -> Event:
        """加入週期性事件（如每週例行行事）"""
        event = Event()
        event.add('summary', name)
        event.add('description', description)
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        event.add('dtstart', start.strftime('%Y%m%d'))
        event.add('dtend', (start + timedelta(days=1)).strftime('%Y%m%d'))
        event.add('dtstamp', start)
        
        # 設定重複規則
        event.add('rrule', {'freq': frequency, 'until': datetime.strptime(until, '%Y%m%d')})
        
        self.calendar.add(event)
        return event
    
    def generate_ics(self, filename: str = 'school_calendar.ics'):
        """產生 ICS 檔案"""
        ics_content = self.calendar.to_unicode()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(ics_content)
        print(f"✅ 已產生 {filename}")
        return filename
    
    def generate_ics_bytes(self) -> bytes:
        """產生 ICS 檔案位元組"""
        return self.calendar.to_ical()

def holidays_to_calendar(holidays_data: List[Dict], school_name: str = "臺灣學校") -> CalendarGenerator:
    """將假期資料轉換為行事曆"""
    generator = CalendarGenerator(school_name)
    
    for entry in holidays_data:
        date_str = entry.get('date', '')
        name = entry.get('name', '')
        is_holiday = entry.get('isHoliday', False)
        
        if is_holiday and date_str and name:
            generator.add_holiday(
                date_str=date_str,
                name=name,
                description=entry.get('description', '')
            )
    
    return generator

def create_sample_calendar():
    """建立範例行事曆"""
    generator = CalendarGenerator("示範學校")
    
    # 加入一些範例事件
    sample_events = [
        ('20250901', '開學日', '新學期開始'),
        ('20250928', '中秋節', '中秋節連假'),
        ('20251010', '國慶日', '國慶日放假'),
        ('20260101', '開國紀念日', '新年放假'),
        ('20260211', '開學日', '第二學期開始'),
        ('20260227', '和平紀念日', '和平紀念日放假'),
        ('20260403', '兒童節', '兒童節放假'),
        ('20260404', '清明節', '清明節放假'),
    ]
    
    for date, name, desc in sample_events:
        generator.add_holiday(date, name, desc)
    
    filename = generator.generate_ics('data/sample_calendar.ics')
    return filename

if __name__ == "__main__":
    print("📅 產生範例學校行事曆...")
    create_sample_calendar()