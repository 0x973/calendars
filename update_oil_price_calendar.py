import datetime
from icalendar import Calendar, Event
from chinese_calendar import is_holiday, is_workday

def add_workdays(start_date, workdays):
    # 如果将到下一年，则直接返回
    if start_date.month == 12 and start_date.day + workdays > 31:
        return datetime.datetime(start_date.year + 1, 1, 1)

    current_date = start_date
    days_added = 0
    while days_added < workdays:
        current_date += datetime.timedelta(days=1)
        if is_workday(current_date):
            days_added += 1
    return current_date

# 定义年份和首次调整日期
year = datetime.datetime.now().year
first_adjustment_date = datetime.datetime(2024, 1, 3)  # 设定首次调整日期

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
with open(f'oil_price_adjustment.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"iCalendar file 'oil_price_adjustment.ics' created successfully!")
