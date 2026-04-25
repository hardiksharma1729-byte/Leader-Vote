from flask import Flask, render_template, request, jsonify, session
import json
import os

app = Flask(__name__)
app.secret_key = "numy_pie_2026_secret"

# File paths
STATS_FILE = "stats.json"
VISITORS_FILE = "visitors.json"


def load_json(filename, default_data):
    """Safe JSON loader"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Load error {filename}: {e}")
    return default_data


def save_json(filename, data):
    """Safe JSON saver"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error {filename}: {e}")


# Initial defaults
stats_data = {"battles": 0, "bhagat": 0, "mahatma": 0}
visitors_data = {"visitors": 0}

stats = load_json(STATS_FILE, stats_data)
visitors = load_json(VISITORS_FILE, visitors_data)


@app.route('/')
def home():
    global visitors
    visitors["visitors"] = visitors.get("visitors", 0) + 1
    save_json(VISITORS_FILE, visitors)

    return render_template('index.html',
                           clicks={
                               "bhagat": stats["bhagat"],
                               "mahatma": stats["mahatma"]
                           },
                           visitors=visitors["visitors"])


@app.route('/vote', methods=['POST'])
def vote():
    # We don't block based on cookie/session anymore
    # (so you can vote again after page refresh)

    data = request.get_json()
    team = data.get('team')

    # Only allow valid teams
    if team != 'bhagat' and team != 'mahatma':
        return jsonify({"status": "invalid_team"}), 400

    if team == 'bhagat':
        stats["bhagat"] += 1
    elif team == 'mahatma':
        stats["mahatma"] += 1

    stats["battles"] += 1
    save_json(STATS_FILE, stats)

    return jsonify({
        "status": "success",
        "bhagat_clicks": stats["bhagat"],
        "mahatma_clicks": stats["mahatma"]
    })


@app.route('/live-stats')
def live_stats():
    return jsonify({
        "bhagat_clicks": stats["bhagat"],
        "mahatma_clicks": stats["mahatma"]
    })


@app.route('/admin')
def admin():
    if request.args.get('key') != '1782':
        return 'Access Denied', 403

    return f"""
    <h1 style='color:#ff0066'>NUMY PIE STATS</h1>
    <p>Bhagat: {stats['bhagat']} | Gandhi: {stats['mahatma']} | Battles: {stats['battles']}</p>
    <a href='/reset?key=1782'>Reset All</a> | <a href='/'>Home</a>
    """


@app.route('/reset')
def reset():
    global stats, visitors
    if request.args.get('key') == '1782':
        stats = {"battles": 0, "bhagat": 0, "mahatma": 0}
        visitors = {"visitors": 0}
        save_json(STATS_FILE, stats)
        save_json(VISITORS_FILE, visitors)
        return 'RESET DONE'
    return 'No access', 403


@app.route('/<path:path>')
def fallback(path):
    return """
    <h1>Page Under Construction</h1>
    <a href='/'>← Back to Battle</a>
    """

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/feedback.html')
def feedback():
    return render_template('feedback.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/idea.html')
def idea():
    return render_template('idea.html')    


if __name__ == '__main__':
    print('🚀 NUMY PIE Starting on http://localhost:5000')
    print('🔥 Admin: http://localhost:5000/admin?key=1782')
    app.run(debug=True)