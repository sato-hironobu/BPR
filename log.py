import sqlite3
from datetime import datetime
import sys

DB_FILE = "./db/bp_data.db"

def init_db():
    """
    Initializes the local SQLite database to store blood pressure and pulse records.

    The database will contain a table named 'records' with the following fields:

    - id (INTEGER): A unique, auto-incremented identifier for each measurement entry.
    - timestamp (TEXT): The date and time when the measurement was taken.
    - systolic (INTEGER): The systolic blood pressure (often called the "top" or "maximum" number), 
      representing the pressure in the arteries when the heart contracts and pumps blood. 
      This value reflects the maximum force your heart exerts on the walls of your arteries.
    - diastolic (INTEGER): The diastolic blood pressure (the "bottom" number), indicating the pressure 
      in the arteries when the heart is at rest between beats. This reflects the baseline arterial tension.
    - pulse (INTEGER): The heart rate in beats per minute (bpm), representing how many times the heart 
      beats in one minute. Pulse provides additional insight into cardiovascular condition and autonomic activity.
    - time_period (TEXT): A textual label for the time of day when the measurement was taken, such as 
      'morning' or 'evening'. This allows tracking of diurnal variation in blood pressure and pulse.

    This structure is designed to support long-term health tracking and to help detect patterns 
    related to hypertension, stress, medication effects, and overall cardiovascular fitness.
    """
    
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
