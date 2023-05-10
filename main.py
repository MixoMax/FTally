from flask import Flask, render_template, url_for
import sqlite3
import os
import json
import time
import csv



class Counter():
    def __init__(self, t_start, db_path = "database.db", source = "Dev"):
        
        self.source = source
        
        self.count = 0
        self.t_start = t_start
        
        self.total_plus = 0
        self.total_minus = 0
        
        
        
        if os.path.exists(db_path):
            self.db = Database(db_path)
            print("Database exists")
            self.count = self.db.cur.execute("SELECT count FROM counter ORDER BY id DESC LIMIT 1").fetchone()[0]
            self.total_plus = self.db.cur.execute("SELECT total_plus FROM counter ORDER BY id DESC LIMIT 1").fetchone()[0]
            self.total_minus = self.db.cur.execute("SELECT total_minus FROM counter ORDER BY id DESC LIMIT 1").fetchone()[0]
            self.t_start = self.db.cur.execute("SELECT timestamp FROM counter ORDER BY id ASC LIMIT 1").fetchone()[0]
            print(self.t_start)
        else:
            self.db = Database(db_path)
            self.db.register(self.count, self.t_start, 0, self.source, self.total_plus, self.total_minus)
    
    def add(self):
        self.count += 1
        self.total_plus += 1
        timestamp = time.time()
        timestamp_rel = timestamp - self.t_start
        
        self.db.register(self.count, timestamp, timestamp_rel, self.source, self.total_plus, self.total_minus)
        
    
    def sub(self):
        self.count -= 1
        self.total_minus += 1
        timestamp = time.time()
        timestamp_rel = timestamp - self.t_start
        
        self.db.register(self.count, timestamp, timestamp_rel, self.source, self.total_plus, self.total_minus)
    
    def export_csv(self):
        self.db.export_csv()


class Database():
    def __init__(self, path = "database.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS counter (id INTEGER PRIMARY KEY, count INTEGER, timestamp float, timestamp_rel float, source TEXT, total_plus INTEGER, total_minus INTEGER)")
        self.conn.commit()
    
    def register(self, count, timestamp, timestamp_rel, source, total_plus, total_minus):
        self.cur.execute("INSERT INTO counter VALUES (NULL, ?, ?, ?, ?, ?, ?)", (count, timestamp, timestamp_rel, source, total_plus, total_minus))
        self.conn.commit()
    
    def export_csv(self):
        """Export the database to a csv file"""
        
        csv_path = self.path.split(".")[0] + ".csv"
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "count", "timestamp", "timestamp_rel", "source", "total_plus", "total_minus"])
            for row in self.cur.execute("SELECT * FROM counter"):
                writer.writerow(row)
    

class Flask_server():
    def __init__(self):
        self.app = Flask(__name__)
        self.counter = Counter(time.time(), source = "Flask", db_path = "database.db")
        
        @self.app.route("/")
        def index():
            return render_template("index.html", count = self.counter.count)
        
        @self.app.route("/script.js")
        def script():
            return url_for("static", filename="script.js")
        
        @self.app.route("/add", methods=["POST"])
        def add():
            self.counter.add()
            return self.counter.count, 200
        
        @self.app.route("/sub", methods=["POST"])
        def sub():
            self.counter.sub()
            return self.counter.count, 200
        
        @self.app.route("/csv", methods=["GET"])
        def csv():
            self.counter.export_csv()
            return url_for("static", filename="database.csv"), 200


if __name__ == "__main__":
    server = Flask_server()
    server.app.run(host="0.0.0.0", port=80, debug=False)