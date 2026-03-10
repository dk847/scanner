from flask import Flask, request
from flask_cors import CORS

from business import handle_flask_api_call


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


@app.route("/scanner", methods=["POST"])
def scan_manifest():
    report = handle_flask_api_call(file=request.files["file"])

    if request.form["is_json"] == "true":
        return report["json"]

    return report["text"]


if __name__ == "__main__":
    app.run(debug=True, port=8000)
