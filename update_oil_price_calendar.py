import os, time
from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
from chinese_calendar import is_holiday, is_workday
import requests

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

def get_92oil_price(region_names):
    url = 'https://v2.xxapi.cn/api/oilPrice'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, headers=headers, timeout=6.0)
        response.raise_for_status()
        data = response.json().get('data', [])
        result = {}
        for region in region_names:
            for item in data:
                if item.get('regionName') == region:
                    result[region] = {'price': item.get('n92', 0), 'priceChange': item.get('n92Change', 0)}
                    break  # 找到第一个匹配的数据后跳出循环
        return result
    except (requests.RequestException, ValueError, KeyError):
        return None

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

def create_oil_price_adjustment_calendar(first_adjustment_date, year):
    cal = Calendar()
    cal.add('prodid', '-//Oil Price Adjustment Calendar//example.com//')
    cal.add('version', '2.0')

    current_date = first_adjustment_date
    adjustment_count = 0
    current_year = current_date.year

    while current_date.year <= year:
        if current_date.year != current_year:
            current_year = current_date.year
            adjustment_count = 0

        if is_workday(current_date):
            adjustment_count += 1
            description = f'这是今年第{adjustment_count}次油价调整'
            dtstart = current_date.replace(hour=23, minute=59, second=59)
            dtend = (current_date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
            event = new_event('油价调整', dtstart, dtend, description)
            cal.add_component(event)

            current_date = add_workdays(current_date, 10)
        else:
            current_date += timedelta(days=1)

    return cal

def add_today_oil_price_event(cal, datas, regions):
    dtstart = date.today()
    dtend = dtstart + timedelta(days=1)
    description = "\n".join([f"{region}92号汽油{datas.get(region, {}).get('price', 0)}元/升，较上次调整{datas.get(region, {}).get('priceChange', 0)}元/升" for region in regions])
    event = new_event('今日油价', dtstart, dtend, description)
    cal.add_component(event)

# 定义年份和首次调整日期
year = datetime.now().year
first_adjustment_date = datetime(2024, 1, 3)  # 设定首次调整日期

# 创建油价调整日历
cal = create_oil_price_adjustment_calendar(first_adjustment_date, year)

# 获取油价数据并添加到日历中
regions = ['天津市', '河北省', '江苏省', '浙江省']
datas = get_92oil_price(regions)
if datas is None:
    datas = get_92oil_price(regions)
if datas:
    add_today_oil_price_event(cal, datas, regions)

# 将iCalendar内容写入文件
with open(f'oil_price_adjustment.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"iCalendar file 'oil_price_adjustment.ics' created successfully!")
