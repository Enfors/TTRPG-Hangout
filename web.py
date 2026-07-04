from flask import Flask, abort, render_template, request, send_from_directory, Response, send_file
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

######## Data

# NPC Appearance generator

APPEARANCE_DATA = {
    "height": [
        (1, "Very short"), (3, "Short"), (7, "Somewhat short"),
        (13, "Average"), (17, "Somewhat tall"), (19, "Tall"), (20, "Very tall")
    ],
    
    "size": [
        # Format: (Max Roll, "Text", Size Mod)
        (1, "Very small", -3), (3, "Small", -2), (7, "Somewhat small", -1),
        (13, "Average", 0), (17, "Somewhat large", 1), (19, "Large", 2), (20, "Very large", 3)
    ],
    
    "proportions": [
        # Format: (Max Roll, "Text") 
        (1, "Extremely small"), (2, "Very small"), (3, "Small"),
        (4, "Somewhat small"), (5, "Average"), (6, "Somewhat large"),
        (7, "Large"), (8, "Very large"), (99, "Extremely large") 
    ],
    
    "eye_color": [
        (2, "Light blue"), (4, "Blue"), (5, "Grey"), (7, "Brown"),
        (9, "Dark brown"), (10, "Green")
    ],
    
    "skin_color": [
        (5, "Western"), (7, "African"), (8, "Asian")
    ],
    
    "hair_color": [
        (2, "Blonde"), (5, "Brown"), (7, "Auburn"), (8, "Red"), (10, "Dark")
    ],
    
    "hair_length": [
        (2, "short"), (3, "shoulder length"), (5, "long"), (6, "very long")
    ],
    
    "hair_style": [
        (2, "loose"), (4, "pony tail"), (5, "bun"), (7, "braided"),
        (9, "half-up, half-down"), (10, "dreadlocks")
    ],
    
    "facial_hair": [
        (5, "None"), (7, "Beard"), (8, "Mustache"), (10, "Sideburns"),
        (11, "Mutton chops"), (12, "Goatee")
    ]
}

SPECIAL_FEATURES = [
    "Facial scar", 
    "Facial birth mark", 
    "Piercings", 
    "Tattoos",
    "Prominent nose", 
    "Distinctive eyebrows", 
    "Freckles", 
    "Thin lips",
    "Full lips", 
    "High cheekbones", 
    "Round face", 
    "Piercing gaze",
    "Wide nose", 
    "Protruding ears", 
    "Cleft chin", 
    "Deep dimples",
    "Pockmarked skin", 
    "Square jaw", 
    "Missing tooth", 
    "Broken/misshaped nose"
]
    
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

@app.route("/gen_yes_no_oracle", methods=["POST"])
def gen_yes_no_oracle():
    # Tuple format: (Max Roll to hit this result, "Text", CSS Column Index)
    yes_no_data = {
        6: [(2, "No and", 3), (3, "No", 4), (4, "No but", 5), (7, "Yes but", 6), (16, "Yes", 7), (20, "Yes and", 8)],
        5: [(2, "No and", 3), (4, "No", 4), (5, "No but", 5), (8, "Yes but", 6), (16, "Yes", 7), (20, "Yes and", 8)],
        4: [(2, "No and", 3), (5, "No", 4), (6, "No but", 5), (9, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        3: [(2, "No and", 3), (6, "No", 4), (7, "No but", 5), (9, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        2: [(2, "No and", 3), (6, "No", 4), (8, "No but", 5), (10, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        1: [(3, "No and", 3), (7, "No", 4), (9, "No but", 5), (11, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        0: [(3, "No and", 3), (8, "No", 4), (10, "No but", 5), (12, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        -1: [(3, "No and", 3), (9, "No", 4), (11, "No but", 5), (13, "Yes but", 6), (17, "Yes", 7), (20, "Yes and", 8)],
        -2: [(3, "No and", 3), (10, "No", 4), (12, "No but", 5), (14, "Yes but", 6), (18, "Yes", 7), (20, "Yes and", 8)],
        -3: [(3, "No and", 3), (11, "No", 4), (13, "No but", 5), (14, "Yes but", 6), (18, "Yes", 7), (20, "Yes and", 8)],
        -4: [(3, "No and", 3), (11, "No", 4), (14, "No but", 5), (15, "Yes but", 6), (18, "Yes", 7), (20, "Yes and", 8)],
        -5: [(4, "No and", 3), (12, "No", 4), (15, "No but", 5), (16, "Yes but", 6), (18, "Yes", 7), (20, "Yes and", 8)],
        -6: [(4, "No and", 3), (13, "No", 4), (16, "No but", 5), (17, "Yes but", 6), (18, "Yes", 7), (20, "Yes and", 8)],
    }

    # Get the user input and roll the dice
    modifier = int(request.form.get("modifier", 0))
    roll = random.randint(1, 20)

    if (roll == 1 or roll == 20): # If random event

        if (roll == 1):
            event_polarity = "Negative"
        else:
            event_polarity = "Positive"

        event_roll = random.randint(1, 4)
        event_type = ["PC", "NPC", "faction", "plot"][event_roll - 1]

        css_injection = f"""
        <style>
            #oracle-random-event tbody tr:nth-child({event_roll}) > *:nth-child(2) {{
                background-color: #b3d0b1 !important;
                box-shadow: inset 2px 2px 10px rgba(0, 0, 0, 0.8) !important;
                font-weight: bold;
            }}
        </style>
        """
        return f"<p><strong>Rolled {roll}, then {event_roll}:</strong> "\
            f"{event_polarity} {event_type} event</p>\n{css_injection}"

    # It's not a random event (roll isn't 1 or 20)
        
    # Calculate the CSS row
    target_row = 7 - modifier

    # Evaluate roll using our yes/no data
    row_data = yes_no_data.get(modifier, [])
    result_text = "Error"
    target_col = 0

    for max_val, text, col_index in row_data:
        if roll <= max_val:
            result_text = text
            target_col = col_index
            break

    # Generate the response with dynamic CSS
    css_injection = f"""
    <style>
        #oracle-yes-no tbody tr:nth-child({target_row}) > *:nth-child({target_col}) {{
            background-color: #b3d0b1 !important;
            box-shadow: inset 2px 2px 10px rgba(0, 0, 0, 0.8) !important;
            font-weight: bold;
        }}
    </style>
    """
    
    return f"<p><strong>Rolled {roll}:</strong> {result_text}</p>\n{css_injection}"

@app.route("/gen_npc_personality", methods=["POST"])
def gen_npc_personality():

    descriptors = {
        "Openness": [
            ["Authoritarian", "Intolerant", "Cynical", "Narrow-minded"],
            ["Inflexible", "Pessimistic", "Hard-headed", "Prejudiced"],
            ["Dogmatic", "Conservative", "Stubborn", "Traditional"],
            ["Skeptical", "Resistant", "Realistic", "Pragmatic"],
            ["Unbiased", "Receptive", "Open-minded", "Curious"],
            ["Philosophical", "Flexible", "Creative", "Inquisitive"],
            ["Tolerant", "Progressive", "Optimistic", "Adventurous"]
        ],
        "Conscientiousness": [
            ["Negligent", "Irresponsible", "Careless", "Lazy"],
            ["Hedonistic", "Impulsive", "Disorganized", "Unreliable"],
            ["Procrastinating", "Impatient", "Unorganized", "Indecisive"],
            ["Distracted", "Casual", "Practical", "Diligent"],
            ["Punctual", "Patient", "Responsible", "Dependable"],
            ["Disciplined", "Thorough", "Efficient", "Goal-oriented"],
            ["Ambitious", "Persevering", "Methodical", "Perfectionist"]
        ],
        "Extraversion": [
            ["Solitary", "Reclusive", "Private", "Withdrawn"],
            ["Reserved", "Shy", "Introspective", "Independent"],
            ["Submissive", "Reflective", "Quiet", "Serious"],
            ["Aloof", "Contemplative", "Ambivert", "Easy-going"],
            ["Outgoing", "Sociable", "Expressive", "Lively"],
            ["Jovial", "Cheerful", "Listener", "Bubbly"],
            ["Energetic", "Passionate", "Flamboyant", "Flirtatious"]
        ],
        "Agreeableness": [
            ["Cruel", "Greedy", "Deceptive", "Manipulative"],
            ["Selfish", "Boastful", "Jealous", "Cynical"],
            ["Rude", "Sarcastic", "Vain", "Competitive"],
            ["Arrogant", "Argumentative", "Polite", "Diplomatic"],
            ["Cooperative", "Trusting", "Honest", "Loyal"],
            ["Kind", "Caring", "Compassionate", "Generous"],
            ["Humorous", "Forgiving", "Charming", "Altruistic"]
        ],
        "Neuroticism": [
            ["Serene", "Stoic", "Hardy", "Poised"],
            ["Grounded", "Calm", "Adaptable", "Sensible"],
            ["Confident", "Focused", "Stable", "Resilient"],
            ["Relaxed", "Concerned", "Restless", "Fickle"],
            ["Wary", "Tense", "Anxious", "Vulnerable"],
            ["Sensitive", "Irritable", "Moody", "Nervous"],
            ["Insecure", "Self-critical", "Depressed", "Panicky"]
        ]
    }

    html = "<table>\n<thead><tr><th>Aspect</th><th>Value</th><th>Descriptor</th></tr></thead>\n"
    aspects = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness",
               "Neuroticism"]
    for aspect in aspects:
        aspect_val = random.randint(1, 7)
        descriptor = random.choice(descriptors[aspect][aspect_val - 1])
        html += f"<tr><td>{aspect}</td><td align=right>{aspect_val}</td><td>{descriptor}</td></tr>\n"

    html += "</table>\n"

    return html

@app.route("/gen_agenda", methods=["POST"])
def gen_agenda():
    goal = [
        "Acquire", "Avenge", "Betray", "Conceal", "Conquer",
        "Destroy", "Discover", "Escape", "Expand", "Explore",
        "Gather", "Glorify", "Infiltrate", "Lead", "Learn",
        "Oppose", "Prevent", "Reconcile", "Restore", "Worship"
    ]

    focus = [
        "Adversary", "Artefact", "Beast", "Child", "Enemy",
        "Idea", "Knowledge", "Location", "Love", "Neighbor",
        "NPC", "Parent", "PC", "Relationship", "Relative",
        "Revenge", "Reward", "Ruler", "Structure", "Wealth"
    ]

    obstacle = [
        "Alliance", "Conflict", "Conflicting interests", "Criminal past", "Distance",
        "Duty", "Family", "Forbidden love", "Health", "Honor",
        "Hostility", "Lack of information", "Lack of resources", "Law", "Love",
        "Mysterious circumstances", "Oath", "Opposing faction", "Pursuers", "Time"
    ]

    html = "%s %s, but %s" % (random.choice(goal), random.choice(focus), random.choice(obstacle))
    
    return f"<p><strong>Agenda:</strong> {html}</p>"

@app.route("/gen_npc_appearance", methods=["POST"])
def gen_npc_appearance():
    detail_level = request.form.get("detail_level")
    allow_facial_hair = request.form.get("allow_facial_hair") == "on"
    
    html = "<table>\n<thead><th>Aspect</th><th>Appearance</th></tr></thead>\n"

    # Height
    height = get_appearance_text("height", random.randint(1, 20))
    html += gen_table_row(["Height", height])

    # If we want size
    if (detail_level == "size" or detail_level == "proportions"):
        size_roll = random.randint(1, 20)
        for max_val, text, size_mod in APPEARANCE_DATA["size"]:
            if size_roll <= max_val:
                size = text
                #print(f"size_mod: {size_mod}")
                break;

        html += gen_table_row(["Size", size])

        # If we want romantic proportions
        if (detail_level == "proportions"):
            for part in ["Chest", "Waist", "Bottom"]:
                part_roll = random.randint(1, 4) + random.randint(1, 4) + size_mod
                #print(f"{part} roll: {part_roll}")
                part_text = get_appearance_text("proportions", part_roll)
                html += gen_table_row([part, part_text])

    # Eye color
    eye_color = get_appearance_text("eye_color", random.randint(1, 10))
    html += gen_table_row(["Eye color", eye_color])

    # Skin color
    skin_color_roll = random.randint(1, 8)
    skin_color = get_appearance_text("skin_color", skin_color_roll)
    html += gen_table_row(["Skin color", skin_color])

    # Hair color
    if (skin_color_roll > 5):  # If African or Asian skin color
        hair = "Dark"
    else:
        hair = get_appearance_text("hair_color", random.randint(1, 10))

    # Hair length
    hair_length_roll = random.randint(1, 6)
    hair += ", " + get_appearance_text("hair_length", hair_length_roll)

    # Long hair style
    if hair_length_roll > 3:  # If long hair
        hair += ", " + get_appearance_text("hair_style", random.randint(1, 10))

    html += gen_table_row(["Hair", hair])

    # Facial hair
    if allow_facial_hair:
        facial_hair = get_appearance_text("facial_hair", random.randint(1, 12))
        html += gen_table_row(["Facial hair", facial_hair])

    # Special features
    html += gen_table_row(["Special features", random.choice(SPECIAL_FEATURES)])
    
    html += "</table>\n"

    return html

def get_appearance_text(aspect, roll):
    data = APPEARANCE_DATA[aspect]
    
    for max_val, text in data:
        if roll <= max_val:
            return text
    return f"(Broken table - roll: {roll})"

def gen_table_row(row):
    output = ""
    
    for col in row:
        output += f"<td>{col}</td>"

    return f"<tr>{output}</tr>\n"

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

