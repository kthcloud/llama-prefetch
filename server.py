from flask import Flask

import threading
import requests
import json
from flask_cors import CORS
import sys
import datetime

app = Flask(__name__)
CORS(app)

body = json.dumps({"prompt": "This is a conversation between user and llama, a friendly chatbot. respond in simple markdown.\n\nUser: Write a new header and subheader for our website, kthcloud. It is a cloud computing service for students and researchers at KTH, the royal institute of technology in stockholm, sweden. Keep it short - one sentence long. Return as a JSON with the header as the \"header\" and \"sub\" objects. \n\n\nllama: {\"header\": \"Welcome to kthcloud\", \"sub\": \"Start deploying your projects today\"}\n\nUser: Another one?\n\n\nllama:",
                  "frequency_penalty": 0, "n_predict": 400, "presence_penalty": 0, "repeat_last_n": 256, "repeat_penalty": 1.18, "stop": ["</s>", "llama:", "User:"], "temperature": 0.7, "tfs_z": 1, "top_k": 40, "top_p": 0.5, "typical_p": 1})

latest_query = {"header": "Welcome to kthcloud",
                "sub": "Start deploying your projects today"}
fetching = False


def log(message, level="INFO"):
    iso = datetime.datetime.now().isoformat()
    print(f"{iso} [{level}] {message}", file=sys.stderr)


def fix_case(string):
    low_str = string.lower()
    index = low_str.find("kthcloud")
    if index == -1:
        return string
    return string[:index] + "kthcloud" + string[index+8:]


@app.route('/query')
def query():
    global latest_query, fetching
    if not fetching:
        fetch_query_thread = threading.Thread(target=fetch_query)
        fetch_query_thread.start()

    return json.dumps(latest_query)


@app.route('/')
def index():
    return "llama-prefetch"


@app.route('/healthz')
def healthz():
    return "ok"


def fetch_query():
    global latest_query, fetching
    fetching = True
    try:
        response = requests.post(
            "https://llama.app.cloud.cbh.kth.se/completion", data=body)
        res_json = response.json()
        content = json.loads(res_json['content'])

        header = fix_case(content['header'])
        sub = fix_case(content['sub'])

        latest_query = {"header": header, "sub": sub}
        log(f"Latest query: {latest_query}")

    except Exception as e:
        log(f"Error fetching query {e}", "ERROR")
    finally:
        fetching = False


if __name__ == '__main__':
    log("Starting server")
    fetch_query()
    app.run('0.0.0.0', 8080)
