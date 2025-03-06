import os, time
from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
from chinese_calendar import is_holiday, is_workday
import requests

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

def get_tj_92_price(regionName):
    url = 'https://v2.xxapi.cn/api/oilPrice'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=6.0)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                if item.get("regionName") == regionName:
                    n92 = item.get('n92', 0)
                    n92Change = item.get('n92Change', 0)
                    return n92, n92Change
        return 0, 0
    except (requests.RequestException, ValueError, KeyError):
        return 0, 0

def add_workdays(start_date, workdays):
    # 如果将到下一年，直接返回下一年的第一天
    if start_date.month == 12 and start_date.day + workdays > 31:
        return datetime(start_date.year + 1, 1, 1)

    current_date = start_date
    days_added = 0
    while days_added < workdays:
        current_date += timedelta(days=1)
        if is_workday(current_date):
            days_added += 1
    return current_date

def new_event(summary, dtstart, dtend, description):
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event.add('description', description)
    return event

# 定义年份和首次调整日期
year = datetime.now().year
first_adjustment_date = datetime(2024, 1, 3)  # 设定首次调整日期

# 初始化iCalendar内容
cal = Calendar()
cal.add('prodid', '-//Oil Price Adjustment Calendar//example.com//')
cal.add('version', '2.0')

# 生成每10个工作日的事件
current_date = first_adjustment_date
adjustment_count = 0
current_year = current_date.year

while current_date.year <= year:
    if current_date.year != current_year:
        current_year = current_date.year
        adjustment_count = 0  # 重置调整计数器

    if is_workday(current_date):
        adjustment_count += 1
        description = f'这是今年第{adjustment_count}次油价调整'
        dtstart = current_date.replace(hour=23, minute=59, second=59)
        dtend = (current_date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        event = new_event('油价调整', dtstart, dtend, description)
        cal.add_component(event)

        # 移动到下一个第10个工作日
        current_date = add_workdays(current_date, 10)
    else:
        current_date += timedelta(days=1)

price, priceChange = get_tj_92_price('天津市')
if price != 0 and priceChange != 0:
    dtstart = date.today()
    dtend = dtstart + timedelta(days=1)
    event = new_event('今日92号油价', dtstart, dtend, f"当前天津市92号汽油{price}元/升，较上次调整{priceChange}元/升")
    cal.add_component(event)

# 将iCalendar内容写入文件
with open(f'oil_price_adjustment.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"iCalendar file 'oil_price_adjustment.ics' created successfully!")
