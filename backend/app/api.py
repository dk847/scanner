from flask import Flask, request
from flask_cors import CORS

from business import handle_flask_api_call
from constants import FE_BASE_URL


app = Flask(__name__)
CORS(app, origins=[FE_BASE_URL])


@app.route("/scanner", methods=["POST"])
def scan_manifest():
    advisories_to_ignore = (
        request.form.get("advisories_to_ignore", "")
        .replace(" ", "")
        .split(",")
    )

    report = handle_flask_api_call(
        file=request.files["file"],
        advisories_to_ignore=advisories_to_ignore,
    )

    if request.form["is_json"] == "true":
        return report["json"]

    return report["text"]


if __name__ == "__main__":
    app.run(debug=True, port=8000)
