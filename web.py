from flask import Flask, abort, render_template, send_from_directory, Response, send_file
import json, os, random

from bs4 import BeautifulSoup

TOC_FILE_NAME = "toc_ttrpg_hangout.html"
INTRO_FILE_NAME = "intro_ttrpg_hangout.html"
MANIFEST_FILE_NAME = "manifest.json"

app = Flask(__name__)
ARTICLE_DIR = "/home/enfors/www"
IMAGES_DIR = os.path.join(ARTICLE_DIR, "images")

MANIFEST_PATH = os.path.join(ARTICLE_DIR, MANIFEST_FILE_NAME)

# Startup
with open (MANIFEST_PATH, 'r') as f:
    manifest_data = json.load(f)

# Routes
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

    # Get article metadata:
    article_metadata = manifest_data.get(html_file_name, {})
    article_tags     = article_metadata.get("tags", [])
    
    # Set use_htmx to True if "htmx" is in the tags list:
    use_htmx = "htmx" in article_tags

    try:
        article_html, title = read_html_and_title(html_file_name)
    except FileNotFoundError:
        abort(404)

    transp_footer_html = read_html("transparency_footer_ttrpg_hangout.html")

    return render_template("article.html", article_html=article_html, title=title,
                           transp_footer_html=transp_footer_html,
                           use_htmx=use_htmx)

# This route mimics PythonAnywhere's static file serving.
# It allows your local Flask to serve files from the "images" folder.
@app.route("/images/<path:image_file_name>")
def custom_static(image_file_name):
    return send_from_directory(IMAGES_DIR, image_file_name)

# Generator functions
@app.route("/gen_action_theme", methods=["POST"])
def gen_action_theme():
    ACTIONS = [ 'Abandon', 'Create', 'Enhance', 'Interrupt',
                'Relocate', 'Accept', 'Damage', 'Erase', 'Investigate', 'Remove',
                'Accuse', 'Deal', 'Escape', 'Keep', 'Restrict', 'Ambush',
                'Deceive', 'Fabricate', 'Lead', 'Reveal', 'Assault', 'Decide',
                'Fail', 'Learn', 'Ruin', 'Assist', 'Defeat', 'Fear', 'Leverage',
                'Sabotage', 'Attack', 'Defend', 'Fight', 'Locate', 'Save',
                'Avoid', 'Demolish', 'Flee', 'Mediate', 'Search', 'Balance',
                'Deny', 'Follow', 'Mislead', 'Stop', 'Begin', 'Destroy', 'Forget',
                'Negate', 'Talk', 'Believe', 'Detect', 'Fortify', 'Obey', 'Tempt',
                'Betray', 'Determine', 'Gain', 'Observe', 'Terminate', 'Beware',
                'Disable', 'Grow', 'Oppress', 'Value', 'Break', 'Dominate',
                'Halt', 'Promise', 'Venture', 'Build', 'Elaborate', 'Heal',
                'Protect', 'Verify', 'Burn', 'Eliminate', 'Hide', 'Pursue',
                'Vilify', 'Cancel', 'Emerge', 'Hinder', 'Raid', 'Violate',
                'Collect', 'Empower', 'Hurt', 'Raise', 'Warn', 'Collide',
                'Endanger', 'Impersonate', 'Recover', 'Weaken', 'Compete',
                'Engage', 'Implicate', 'Reject', 'Withdraw' ]

    THEMES = [ 'Allegations', 'Discovery', 'Landscape', 'Medicine',
               'Prophet', 'Alliances', 'Doom', 'Language', 'Monsters',
               'Quarrel', 'Allies', 'Dreams', 'Leader', 'Nature', 'Realm',
               'Ambition', 'Emotions', 'Leadership', 'Neglect', 'Rejection',
               'Anger', 'Enemies', 'Legend', 'Night', 'Reward', 'Artifact',
               'Fear', 'Liberty', 'Nightmare', 'Sadness', 'Beginnings',
               'Forest', 'Lies', 'Obligation', 'Science', 'Betrayal',
               'Greatness', 'Light', 'Oblivion', 'Secrets', 'Bonds',
               'Happiness', 'Limitations', 'Occupant', 'Technology',
               'Border', 'Hate', 'Loan', 'Offense', 'Terrain', 'Child',
               'Hidden, the', 'Lock', 'Opportunity', 'Threat', 'Community',
               'Homes', 'Lord', 'Opposition', 'Traitor', 'Consent', 'Hope',
               'Lore', 'Oppression', 'Treason', 'Curse', 'Illusion', 'Love',
               'Passion', 'Truth', 'Darkness', 'Innocent', 'Machine',
               'Peace', 'Unity', 'Desecration', 'Intrigue', 'Madness',
               'Plague', 'Values', 'Desolation', 'Joy', 'Magic', 'Plans',
               'Vandalism', 'Devastation', 'Kind', 'Malice', 'Political, the',
               'Vicinity', 'Devotion', 'Kingdom', 'Mania', 'Possibilities',
               'Vision', 'Disaster', 'Knowledge', 'Master', 'Power', 'War' ]

    action = random.choice(ACTIONS)
    theme = random.choice(THEMES)

    return f"<p><strong>Result:</strong> {action} / {theme}</p>\n"

# Utility functions
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

