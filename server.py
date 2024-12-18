from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import sys
import sqlite3
import csv
from openpyxl import Workbook
from openpyxl.styles import Font
from datetime import datetime

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect('tally.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tally (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        value INTEGER DEFAULT 0,
        timestamp TEXT
    )
''')
conn.commit()


@app.get("/tally")
async def get_tally():
    """Retrieves the current tally value and timestamp."""
    cursor.execute("SELECT value, timestamp FROM tally ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    return JSONResponse({"value": result[0] if result else 0, "timestamp": result[1] if result else None})

@app.post("/tally/increment")
async def increment_tally():
    """Increments the tally value by 1 and stores it in the database."""
    cursor.execute("SELECT value FROM tally ORDER BY id DESC LIMIT 1")
    data = cursor.fetchone()
    if not data:
        last_value = 0
    else:
        last_value = data[0]
    
    new_value = last_value + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO tally (value, timestamp) VALUES (?, ?)", (new_value, timestamp))
    conn.commit()
    return JSONResponse({"message": "Tally incremented"})

@app.post("/tally/decrement")
async def decrement_tally():
    """Decrements the tally value by 1 and stores it in the database."""
    cursor.execute("SELECT value FROM tally ORDER BY id DESC LIMIT 1")
    data = cursor.fetchone()
    if not data:
        last_value = 0
    else:
        last_value = data[0]

    new_value = last_value - 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO tally (value, timestamp) VALUES (?, ?)", (new_value, timestamp))
    conn.commit()
    return JSONResponse({"message": "Tally decremented"})

@app.get("/tally/export/csv")
async def export_csv():
    """Exports the tally data to a CSV file."""
    cursor.execute("SELECT value, timestamp FROM tally")
    data = cursor.fetchall()
    with open("tally.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Value"])
        writer.writerows([(row[1], row[0]) for row in data])
    return FileResponse("tally.csv")

@app.get("/tally/export/xlsx")
async def export_xlsx():
    """Exports the tally data to an XLSX file."""
    cursor.execute("SELECT value, timestamp FROM tally")
    data = cursor.fetchall()
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Timestamp", "Value"])
    for row in data:
        sheet.append((row[1], row[0]))
    
    # Style the header row
    header_font = Font(bold=True)
    for cell in sheet[1]:
        cell.font = header_font

    workbook.save("tally.xlsx")
    return FileResponse("tally.xlsx")



@app.get("/{path:path}")
async def catch_all(path):
    if not path:
        path = "index.html"
    return FileResponse(path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port_num = int(sys.argv[1])
    else:
        port_num = 8000
    
    uvicorn.run(app, host="0.0.0.0", port=port_num)
