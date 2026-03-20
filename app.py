import json
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.json")


def load_db():
    with open(DB_PATH) as f:
        return json.load(f)


db = load_db()


@app.route("/check", methods=["GET"])
def check():
    depno = request.args.get("DEPNO")
    dep_type = request.args.get("TYPE")
    user = request.args.get("USER")

    if not all([depno, dep_type, user]):
        return jsonify({"status": "error", "message": "Missing required parameters: DEPNO, TYPE, USER"}), 400

    entry = next((e for e in db if e["DEPNO"] == depno), None)

    if entry is None:
        return jsonify({"status": "not-valid", "reason": "DEPNO not found"})

    if user not in entry["allowed_users"]:
        return jsonify({"status": "not-valid", "reason": "user not authorized"})

    if dep_type not in entry["allowed_types"]:
        return jsonify({"status": "not-valid", "reason": "type not permitted"})

    return jsonify({
        "status": "valid",
        "DEPNO": depno,
        "TYPE": dep_type,
        "USER": user,
        "time_range": entry["time_range"],
        "allowed_systems": entry["allowed_systems"],
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
