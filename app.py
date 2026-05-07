# 學校行事曆整合系統 - 主應用程式
# 使用 Flask 整合爬蟲、ICS 生成器、LINE Bot 和前端

import os
import json
from datetime import datetime
from flask import Flask, jsonify, Response, send_file, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# 匯入各模組
from scraper.school_calendar_scraper import SchoolCalendarScraper
from icalendar_generator.calendar_generator import CalendarGenerator, holidays_to_calendar

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# 初始化
scraper = SchoolCalendarScraper()
calendar_generator = CalendarGenerator("學校行事曆")

# 確保 data 目錄存在
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/calendar')
def get_calendar():
    """取得所有行事曆事件 (JSON)"""
    try:
        # 嘗試從快取讀取，否則從網路抓取
        cache_file = 'data/holidays_current.json'
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                holidays = json.load(f)
        else:
            # 抓取 2025 年行事曆
            holidays = scraper.get_holiday_data(2025)
            scraper.save_to_json(holidays, cache_file)
        
        return jsonify({
            'success': True,
            'data': holidays,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/holidays')
def get_holidays():
    """取得特定年份假期"""
    year = request.args.get('year', 2025, type=int)
    
    try:
        holidays = scraper.get_holiday_data(year)
        return jsonify({
            'success': True,
            'year': year,
            'holidays': holidays
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/calendar/school.ics')
def get_calendar_ics():
    """取得 ICS 格式行事曆"""
    try:
        # 取得假期資料
        year = request.args.get('year', 2025, type=int)
        holidays = scraper.get_holiday_data(year)
        
        # 轉換為行事曆
        cal_gen = holidays_to_calendar(holidays, "學校行事曆")
        ics_bytes = cal_gen.generate_ics_bytes()
        
        return Response(
            ics_bytes,
            mimetype='text/calendar; charset=utf-8',
            headers={
                'Content-Disposition': f'attachment; filename=school_calendar_{year}.ics'
            }
        )
    except Exception as e:
        return Response(
            f"BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR",
            mimetype='text/calendar; charset=utf-8'
        )

@app.route('/calendar/sample.ics')
def get_sample_ics():
    """取得範例 ICS 檔案"""
    return send_file('data/sample_calendar.ics', mimetype='text/calendar')

@app.route('/api/sync', methods=['POST'])
def sync_calendar():
    """手動同步行事曆"""
    try:
        years = request.json.get('years', [2024, 2025, 2026])
        all_holidays = scraper.get_all_holidays(min(years), max(years))
        
        # 儲存到快取
        scraper.save_to_json(all_holidays, 'data/holidays_current.json')
        
        return jsonify({
            'success': True,
            'synced_years': list(all_holidays.keys()),
            'total_holidays': sum(len(h) for h in all_holidays.values())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'service': 'school-calendar-system',
        'timestamp': datetime.now().isoformat()
    })

# 錯誤處理
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    # 本地開發模式
    app.run(host='0.0.0.0', port=5000, debug=True)