import sqlite3
from datetime import datetime
import sys

DB_FILE = "bp_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            pulse INTEGER,
            time_period TEXT
        )
    ''')
    conn.commit()
    conn.close()

def infer_time_period(timestamp):
    hour = timestamp.hour
    if hour < 10:
        return 'M'
    elif hour >= 18:
        return 'N'
    else:
        return None

def log_bp(systolic, diastolic, pulse, time_period=None):
    now = datetime.now()
    inferred = time_period or infer_time_period(now)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO records (timestamp, systolic, diastolic, pulse, time_period)
        VALUES (?, ?, ?, ?, ?)
    ''', (now.strftime('%Y-%m-%d %H:%M:%S'), systolic, diastolic, pulse, inferred))
    conn.commit()
    conn.close()

    period_str = {
        'M': 'Morning',
        'N': 'Night',
        None: 'Unspecified'
    }[inferred]

    print(f"Recorded: {now} - {systolic}/{diastolic}, Pulse: {pulse} ({period_str})")

if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print("Usage: python log.py <systolic> <diastolic> <pulse> [M|N]")
        sys.exit(1)

    try:
        systolic = int(sys.argv[1])
        diastolic = int(sys.argv[2])
        pulse = int(sys.argv[3])
    except ValueError:
        print("Systolic, diastolic, and pulse must be integers.")
        sys.exit(1)

    time_period = None
    if len(sys.argv) == 5:
        time_period_input = sys.argv[4].upper()
        if time_period_input not in ('M', 'N'):
            print("Time period must be 'M' for Morning or 'N' for Night.")
            sys.exit(1)
        time_period = time_period_input

    init_db()
    log_bp(systolic, diastolic, pulse, time_period)
