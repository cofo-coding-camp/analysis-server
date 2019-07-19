from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.sqlite3'

db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column("record_id",db.Integer,primary_key=True)
    user_name = db.Column(db.String(50))
    file_name = db.Column(db.String(50))
    commit_message = db.Column(db.String(300))
    commit_time = db.Column(db.DateTime())
    __table_args__ = (db.UniqueConstraint('user_name', 'file_name', name='_user_file_uc'),)

    def __init__(self,user_name, file_name, commit_message, commit_time):
        self.user_name = user_name
        self.file_name = file_name
        self.commit_message = commit_message
        self.commit_time = commit_time

@app.route("/")
def index():
    r = Record("123","ab.py","asdas",datetime.datetime.now())
    db.session.add(r)
    db.session.commit()
    return "hello world"

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)