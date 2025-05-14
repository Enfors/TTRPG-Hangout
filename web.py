from flask import Flask, render_template
import os


app = Flask(__name__)
article_dir = "../../RoamNotes"

@app.route("/")
def start():
    return "<h1>Welcome to TTRPG-Hangout.com!</h1>"

@app.route("/article/<string:article_file_name>")
def article(article_file_name):
    if not article_file_name[-5:] == ".html":
        article_file_name += ".html"
    with open(os.path.join(article_dir, article_file_name)) as html_file:
        html = html_file.read()
        return render_template("article.html", html=html)
