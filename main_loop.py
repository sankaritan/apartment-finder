import sys
import threading
import time
import traceback

from flask import Flask, request
from flask_cors import CORS
from flask_jsonpify import jsonify

import settings
import util
import json

from scraper import do_scrape

app = Flask(__name__)
api = CORS(app)


@app.route("/areas", methods=['GET'])
def get_areas():
    return jsonify(util.get_boxes())


@app.route("/save-areas", methods=['POST'])
def save_areas():
    try:
        content = request.get_json()
        print(content)
        file = open(settings.BOXES_FILE, 'w')
        json_to_save = json.dumps(content, sort_keys=True, indent=4)
        file.write(json_to_save)
        file.close()
        return json_to_save
    except Exception:
        return 'Error: Post went wrong!', 500


def server_api_worker():
    app.run(port='5002')
    return


def scraping_worker():
    while True:
        print("{}: Starting scrape cycle".format(time.ctime()))
        try:
            do_scrape()
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(time.ctime()))
        time.sleep(settings.SLEEP_INTERVAL)


if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=server_api_worker)
        t1.start()
        # t2 = threading.Thread(target=scraping_worker)
        # t2.start()
    except KeyboardInterrupt:
        print("Exiting....")
        sys.exit(1)
