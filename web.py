from flask import Flask, abort, render_template, send_from_directory, Response, send_file
import os

from bs4 import BeautifulSoup

TOC_FILE_NAME = "toc_ttrpg_hangout.html"
INTRO_FILE_NAME = "intro_ttrpg_hangout.html"

app = Flask(__name__)
ARTICLE_DIR = "/home/enfors/www"
IMAGES_DIR = os.path.join(ARTICLE_DIR, "images")

@app.route("/")
def start():
    intro_html = read_html(INTRO_FILE_NAME)
    toc_html = read_html(TOC_FILE_NAME)
        
    return render_template("start.html", intro_html=intro_html, toc_html=toc_html)

@app.route("/atom.xml")
def atom():
    # Have Flask handle MIME type and ETags automatically.
    # This means that feed readers will be able to say "Send me atom.xml, but only
    # if it has been updated since I got it last time."
    return send_from_directory(ARTICLE_DIR, "atom.xml",
                               mimetype="application/atom+xml")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(IMAGES_DIR, "favicon.ico",
                               mimetype="image/vnd.microsoft.icon")

@app.route("/<string:article_file_name>")
def article(article_file_name):

    if article_file_name[-5:] == ".html":
        article_file_name = article_file_name[:-5]

    html_file_name = article_file_name + ".html"

    try:
        article_html, title = read_html_and_title(html_file_name)
    except FileNotFoundError:
        abort(404)

    transp_footer_html = read_html("transparency_footer_ttrpg_hangout.html")

    return render_template("article.html", article_html=article_html, title=title,
                           transp_footer_html=transp_footer_html)

# This route mimics PythonAnywhere's static file serving.
# It allows your local Flask to serve files from the "images" folder.
@app.route("/images/<path:image_file_name>")
def custom_static(image_file_name):
    return send_from_directory(IMAGES_DIR, image_file_name)

def read_html(file_name):
    with open(os.path.join(ARTICLE_DIR, file_name)) as html_file:
        return html_file.read()

def read_html_and_title(file_name):
    html = read_html(file_name)
    title = None

    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1')

    if h1_tag:
        title = h1_tag.get_text()

    return html, title

