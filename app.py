from flask import Flask, request, jsonify
from db import db, CallInfo
from sqlalchemy import create_engine


app = Flask(__name__)

DB_FILE = "calls_info.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Endpoint POST minimal pour /end-of-call
@app.route("/end-of-call", methods=["POST"])
def end_of_call():
    #Return 200 just to start
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True)