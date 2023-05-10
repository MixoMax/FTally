from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import json
import time
import csv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///counter.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app)



class Counter():
    def __init__(self, t_start, db, source = "Dev-Test"):
        
        latest = db.get_last()
        if latest != False:
            self.count, self.t_start, timestamp_rel, self.source, self.total_plus, self.total_minus = latest
        else:
            self.count = 0
            self.t_start = t_start
            self.source = source
            self.total_plus = 0
            self.total_minus = 0
        self.db = db
    
    
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

class DB_entry(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    count = db.Column("count", db.Integer)
    timestamp = db.Column("timestamp", db.Float)
    timestamp_rel = db.Column("timestamp_rel", db.Float)
    source = db.Column("source", db.String(100))
    total_plus = db.Column("total_plus", db.Integer)
    total_minus = db.Column("total_minus", db.Integer)
    
    def __init__(self, count, timestamp, timestamp_rel, source, total_plus, total_minus):
        self.count = count
        self.timestamp = timestamp
        self.timestamp_rel = timestamp_rel
        self.source = source
        self.total_plus = total_plus
        self.total_minus = total_minus

class DB():
    def __init__(self):
        self.db = db
        self.db.create_all()
    
    def register(self, count, timestamp, timestamp_rel, source, total_plus, total_minus):
        entry = DB_entry(count, timestamp, timestamp_rel, source, total_plus, total_minus)
        self.db.session.add(entry)
        self.db.session.commit()
    
    def get_last(self):
        if DB_entry.query.count() == 0:
            return False
        entry = DB_entry.query.order_by(DB_entry._id.desc()).first()
        return [entry.count, entry.timestamp, entry.timestamp_rel, entry.source, entry.total_plus, entry.total_minus]
    
    def export_csv(self):
        entries = DB_entry.query.all()
        with open("export.csv", "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "count", "timestamp", "timestamp_rel", "source", "total_plus", "total_minus"])
            for entry in entries:
                writer.writerow([entry._id, entry.count, entry.timestamp, entry.timestamp_rel, entry.source, entry.total_plus, entry.total_minus])


counter = Counter(time.time(), DB())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods = ["POST"])
def add():
    counter.add()
    return "OK", 204

@app.route("/sub", methods = ["POST"])
def sub():
    counter.sub()
    return "OK", 204

@app.route("/export", methods = ["POST"])
def export():
    counter.export_csv()
    return "OK", 204

@app.route("/get", methods = ["GET"])
def get():
    return str(counter.count), 200


@app.route("/stylesheet.css")
def stylesheet():
    return app.send_static_file("stylesheet.css")


if __name__ == "__main__":
    app.run(debug = True)