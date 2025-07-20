import sqlite3
import random
from datetime import datetime, timedelta
from log import init_db, DB_FILE

def random_timestamp(start_date, days_range):
    base = datetime.strptime(start_date, '%Y-%m-%d')
    random_day = base + timedelta(days=random.randint(0, days_range - 1))
    random_time = timedelta(hours=random.randint(5, 23), minutes=random.randint(0, 59))
    return (random_day + random_time)

def infer_time_period(hour):
    if hour < 10:
        return 'M'
    elif hour >= 18:
        return 'N'
    else:
        return None

def insert_random_record(c, timestamp):
    systolic = random.randint(100, 150)
    diastolic = random.randint(60, 95)
    pulse = random.randint(55, 90)
    time_period = infer_time_period(timestamp.hour)

    c.execute('''
        INSERT INTO records (timestamp, systolic, diastolic, pulse, time_period)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        systolic,
        diastolic,
        pulse,
        time_period
    ))

def generate_records(n=100, start_date='2025-07-01'):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for _ in range(n):
        ts = random_timestamp(start_date, 31)
        insert_random_record(c, ts)
    conn.commit()
    conn.close()
    print(f"{n} dummy records inserted.")

if __name__ == "__main__":
    generate_records(100)
