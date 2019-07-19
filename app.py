from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.sqlite3'

db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column("record_id",db.Integer,primary_key=True)
    user_name = db.Column(db.String(50))
    commit_message = db.Column(db.String(300))
    commit_time = db.Column(db.DateTime())
    

    def __init__(self,user_name, commit_message, commit_time):
        self.user_name = user_name
        self.commit_message = commit_message
        self.commit_time = commit_time

@app.route("/")
def index():
   
    results = []
    for record in Record.query.all():
        results.append({"id":record.id,"user_name":record.user_name,"commit_message":record.commit_message,"commit_time":record.commit_time.strftime("%Y-%m-%d %H:%M:%S")})
    return json.dumps(results)


@app.route("/push",methods=["POST"])
def push():
    data = json.loads(request.data)
    commits = data["commits"]
    for commit in commits:
        r = Record(commit["author"]["name"],commit["message"],datetime.datetime.now())
        db.session.add(r)
    db.session.commit()
    return "OK"

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)