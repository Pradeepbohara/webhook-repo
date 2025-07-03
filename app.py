from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["github_events"]
collection = db["events"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")

    data = {}

    if event == "push":
        data = {
            "type": "push",
            "message": f"{payload['pusher']['name']} pushed to {payload['ref'].split('/')[-1]} on {timestamp}"
        }

    elif event == "pull_request":
        action = payload["action"]
        if action == "opened":
            data = {
                "type": "pull_request",
                "message": f"{payload['pull_request']['user']['login']} submitted a pull request from {payload['pull_request']['head']['ref']} to {payload['pull_request']['base']['ref']} on {timestamp}"
            }

    elif event == "pull_request" and payload["action"] == "closed" and payload["pull_request"]["merged"]:
        data = {
            "type": "merge",
            "message": f"{payload['pull_request']['user']['login']} merged branch {payload['pull_request']['head']['ref']} to {payload['pull_request']['base']['ref']} on {timestamp}"
        }

    if data:
        collection.insert_one(data)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "ignored"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort("_id", -1).limit(10))
    return jsonify([e['message'] for e in events])

if __name__ == '__main__':
    app.run(debug=True)
