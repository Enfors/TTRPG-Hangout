from flask import Flask, render_template
import os

TOC_FILE_NAME = "toc_ttrpg_hangout.html"

app = Flask(__name__)
ARTICLE_DIR = "../../RoamNotes"

@app.route("/")
def start():
    with open(os.path.join(ARTICLE_DIR, TOC_FILE_NAME)) as toc_file:
        toc_html = toc_file.read()
    
    return render_template("start.html", toc_html=toc_html)

@app.route("/article/<string:article_file_name>")
def article(article_file_name):

    if article_file_name[-5:] == ".html":
        article_file_name = article_file_name[:-5]

    html_file_name = article_file_name + ".html"
        
    with open(os.path.join(ARTICLE_DIR, html_file_name)) as html_file:
        html = html_file.read()

    return render_template("article.html", html=html)
