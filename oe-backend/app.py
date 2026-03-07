import os

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return {"message": "Hello from oe-backend!"}


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
