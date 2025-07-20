import sqlite3
from fpdf import FPDF
from datetime import datetime
import sys

DB_FILE = "./db/bp_data.db"
OUTPUT_FILE = "./pdf/blood_pressure_records.pdf"
FONT_IPAEXGOTHIC_FILE = "./font/ipaexg.ttf"

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font('IPAexGothic', '', FONT_IPAEXGOTHIC_FILE, uni=True)

    def header(self):
        self.set_font("IPAexGothic", "", 16)
        self.cell(0, 10, f"血圧記録 - {self.period_str}", ln=True, align="C")
        self.set_font("IPAexGothic", "", 10)
        self.cell(0, 10, f"作成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("IPAexGothic", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_table(self, data):
        self.set_font("IPAexGothic", "", 12)
        col_widths = [45, 30, 30, 30, 30]
        headers = ["日時", "収縮期", "拡張期", "脈拍", "時間帯"]
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1, align="C")
        self.ln()

        self.set_font("IPAexGothic", "", 12)
        for row in data:
            timestamp, systolic, diastolic, pulse, time_period = row
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            period_str = {
                'M': '朝',
                'N': '夜',
                None: '未設定'
            }.get(time_period, '未設定')

            row_data = [
                timestamp,
                str(systolic),
                str(diastolic),
                str(pulse),
                period_str
            ]
            for i, item in enumerate(row_data):
                self.cell(col_widths[i], 10, item, border=1)
            self.ln()

def fetch_records(year: int, month: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year+1:04d}-01-01"
    else:
        end = f"{year:04d}-{month+1:02d}-01"

    c.execute('''
        SELECT timestamp, systolic, diastolic, pulse, time_period
        FROM records
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp ASC
    ''', (start, end))
    rows = c.fetchall()
    conn.close()
    return rows

def export_to_pdf(data, year, month):
    pdf = PDF()
    pdf.period_str = f"{year}-{month:02d}"
    pdf.add_page()
    if not data:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "No records found for this month.", ln=True)
    else:
        pdf.add_table(data)
    pdf.output(OUTPUT_FILE)
    print(f"PDF saved as: {OUTPUT_FILE}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            yyyymm = sys.argv[1]
            year = int(yyyymm[:4])
            month = int(yyyymm[4:6])
            if not 1 <= month <= 12:
                raise ValueError
        except ValueError:
            print("Please provide the month in 'yyyymm' format.")
            sys.exit(1)
    else:
        now = datetime.now()
        year = now.year
        month = now.month

    records = fetch_records(year, month)
    export_to_pdf(records, year, month)
