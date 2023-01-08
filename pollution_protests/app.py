from flask import Flask, render_template, request, redirect
import subprocess
import requests
import json
from os import path
import os

ROOT = path.realpath(path.join(os.getcwd(), path.dirname(__file__)))
BACKEND = "http://localhost:3000/"

app = Flask(__name__)
app.secret_key = b"{{secret_key}}"
app.challenge_name = "Pollution Protest"
app.flag = "{{flag}}"

NODE_PATH = "/usr/bin/node"
NODE_PATH = "/usr/local/bin/node"

# @app.before_first_request
def init():
    try:
        os.environ["NODE_PATH"] = "/usr/lib/node_modules"
        p = subprocess.Popen([NODE_PATH, "./backend.js"])
        with open(path.join(ROOT, "flag.txt"), "w") as f:
            f.write(f"your flag: {app.flag}")
    except Exception as e:
        pass


@app.route("/", methods=["GET"])
def index():
    try:
        r = requests.get(BACKEND)
        results = json.loads(r.text)
        return render_template("index.html", results=results)
    except:
        return render_template("index.html", error="Cannot connect to message board, contact admin or refresh.")


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "GET":
        return render_template("new.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        messageText = request.form['messageText']
        try:
            headers = {"content-type": "application/json"}
            data = {
                "auth": {"name": username, "password": password},
                "message": {"text": messageText}
            }
            r = requests.put(BACKEND, headers=headers, json=data)
            print(r.text)
        except:
            print(r.text)
        return redirect("/", 303)


@app.route("/modify", methods=["GET", "POST"])
def modify():
    if request.method == "GET":
        return render_template("modify.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        messageID = request.form['messageID']
        messageText = request.form['messageText']
        try:
            headers = {"content-type": "application/json"}
            data = {
                "auth": {"name": username, "password": password},
                "messageId": messageID,
                "messageText": messageText
            }
            r = requests.post(BACKEND, headers=headers, json=data)
            print(r.text)
        except:
            print(r.text)
            print("error")
        return redirect("/", 303)


@app.route("/checker", methods=["GET"])
def checker():
    if request.method == "GET":
        r = requests.get("http://localhost:3000/")
        result = json.loads(r.text)
        targetText = result[0]['text']
        targetId = result[0]['id']
        if targetText == "hack the planet" and targetId == 0:
            return (f"your flag: {str(app.flag)}")
        else:
            return ("no flag for you")


if __name__ == '__main__':
    init()
    app.run(host='localhost', port="5001")