import os

from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from api.algorithm_controller import algorithm_ns

app = Flask(__name__)
CORS(app)

api = Api(
    app,
    version="1.0",
    title="OE Optimization API",
    description="Genetic Algorithm Optimization API",
    doc="/api/docs",
    prefix="/api",
)

api.add_namespace(algorithm_ns)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
