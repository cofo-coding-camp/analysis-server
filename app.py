from flask import Flask 
from flask import request
from sqlalchemy import Date, cast
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from flask import jsonify
from prettytable import PrettyTable

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://b51fa35aa80e09:8c155115@us-cdbr-iron-east-02.cleardb.net/heroku_8862be285234577'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column("record_id",db.Integer,primary_key=True)
    github_name = db.Column(db.String(50))
    commit_message = db.Column(db.String(300))
    file_name = db.Column(db.String(20))
    commit_time = db.Column(db.DateTime())
    

    def __init__(self,github_name,commit_message, file_name, commit_time):
        self.github_name = github_name
        self.file_name = file_name
        self.commit_message = commit_message
        self.commit_time = commit_time

class User(db.Model):
    id = db.Column("user_id",db.Integer,primary_key=True)
    github_name = db.Column(db.String(50))
    wechat_name = db.Column(db.String(50))

    def __init__(self, github_name,wechat_name):
        self.github_name = github_name
        self.wechat_name = wechat_name

@app.route("/")
def index():
    days = request.args.get("days")

    if not days:
        days = "7"
    if not days.isdigit():
        return "Days should be integer!"
    days = int(days)
    if days <1:
        return "Days should be at least 1"
    
    date_base = datetime.datetime.today()
    date_list = [date_base - datetime.timedelta(days=x) for x in range(0, days)]
    date_list.reverse()
    
    
    table = PrettyTable(["Name","Total"] + [date.strftime("%Y-%m-%d") for date in date_list])
    for user in User.query.all():
        total = Record.query.filter(Record.github_name == user.github_name)
        total = total.filter(Record.commit_time <=(date_list[-1]+datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
        total = total.filter(Record.commit_time > (date_list[0]).strftime("%Y-%m-%d"))
        total = total.count()
        date_submisson_times = []
        for date in date_list:
            count = Record.query.filter(Record.github_name==user.github_name)
            count = count.filter(cast(Record.commit_time,Date) == date.strftime("%Y-%m-%d")).count()
            date_submisson_times.append(count)
        table.add_row([user.wechat_name] + [total] + date_submisson_times)   
    return table.get_html_string()

    

@app.route("/records",methods=["GET"])
def records():
    results = []
    for record in Record.query.all():
        id = record.id 
        github_name = record.github_name
        commit_message = record.commit_message
        file_name = record.file_name
        commit_time = record.commit_time.strftime("%Y-%m-%d")
        results.append({"id":id,"github_name":github_name,"commit_message":commit_message, "file_name":file_name, "commit_time":commit_time})
    return json.dumps(results)

@app.route("/push",methods=["POST"])
def push():
    data = json.loads(request.data)
    commits = data["commits"]

    for commit in commits:
        message = commit["message"]
        added = commit["added"]
        if added:
            file_name = added[0]
            r = Record(commit["author"]["name"],message,file_name, datetime.datetime.now())
        db.session.add(r)
    db.session.commit()
    return "OK"

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)