from flask import Flask 
app = Flask(__name__)

@app.router("/")
def index():
    return "hello world"