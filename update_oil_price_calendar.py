import datetime
import calendar
from icalendar import Calendar, Event

def is_workday(date):
    return date.weekday() < 5  # Monday to Friday are workdays

def add_workdays(start_date, workdays):
    current_date = start_date
    days_added = 0
    while days_added < workdays:
        current_date += datetime.timedelta(days=1)
        if is_workday(current_date):
            days_added += 1
    return current_date

# 定义年份和首次调整日期
year = datetime.datetime.now().year
first_adjustment_date = datetime.datetime(2025, 1, 2)  # 设定首次调整日期

# 初始化iCalendar内容
cal = Calendar()
cal.add('prodid', '-//Oil Price Adjustment Calendar//example.com//')
cal.add('version', '2.0')

# 生成每10个工作日的事件
current_date = first_adjustment_date
adjustment_count = 0
while current_date.year == year:
    if is_workday(current_date):
        adjustment_count += 1
        event = Event()
        event.add('summary', '油价调整')
        event.add('dtstart', current_date.replace(hour=23, minute=59, second=59))
        event.add('dtend', (current_date + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0))
        event.add('description', f'这是今年第{adjustment_count}次油价调整。')
        cal.add_component(event)

        # 移动到下一个10个工作日
        current_date = add_workdays(current_date, 10)
    else:
        current_date += datetime.timedelta(days=1)

# 将iCalendar内容写入文件
with open(f'oil_price_adjustment_{year}.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"iCalendar file 'oil_price_adjustment_{year}.ics' created successfully!")
