from flask import Flask, render_template,request,redirect, Response, flash, session
from flask_session import Session
from scripts import mariadb_runner
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import io 
db_runner = mariadb_runner 


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/login", methods=["POST", "GET"])
def login():
  # if form is submited
    if request.method == "POST":
        # record the user name
        session["format"] = request.form.get("name")
        # redirect to the main page
        return redirect("/")
    session["format"] = 'Brawl'
    return redirect("/")
    
    
@app.route("/format/<formatid>", methods=["GET"])
def set_format(formatid):
    session["format"] = formatid
    #redirect to referrer
    ref_url = request.headers.get("Referer")
    if ref_url:
        return redirect(ref_url)
    

    return redirect("/")

@app.route("/topcards")
def top_cards():
    topcards = db_runner.get_topcards(session["format"])
    return render_template('topcards.html', cards=topcards)

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

@app.route("/",  methods=["GET", "POST"])
def main():
      # check if the users exist or not
    if not session.get("format"):
        # if not there in the session then redirect to the login page
        return redirect("/login")
    if request.method == "GET":
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M")
        print(date)
        con = db_runner.connect()
        
        
        db_runner.close_connection(con)
        return redirect("/commanders")
        return render_template('index.html',format = session["format"],date=date)
    
    if request.method == "POST":
        con = db_runner.connect()
        db_runner.close_connection(con)
        # redirect back to the index page
         
        
        return redirect("/")

        
    return render_template('index.html')

@app.route("/commanders", methods=["GET"])
def commanders():
    if not session.get("format"):
        return redirect("/login")
    commanders = db_runner.get_commanders(session["format"])
    return render_template('commanders.html', commanders=commanders)

@app.context_processor
def inject_variable():
    try:
        return dict(format=session["format"])
    except:
        return dict()

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(debug=True, host='0.0.0.0', port=80, threaded=True)