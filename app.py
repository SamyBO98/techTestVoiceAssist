from flask import Flask, request, jsonify
from db import db, CallInfo


app = Flask(__name__)

DB_FILE = "calls_info.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
#No need to track all changes (only insert in our DB)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Endpoint POST minimal pour /end-of-call
@app.route("/end-of-call", methods=["POST"])
def end_of_call():
    data = request.get_json()

    appointment_date = data.get("date", "")
    call_id = data.get("room")
    if not appointment_date:
        return jsonify({"status": "error", "message": "date manquante"}), 400
    call = CallInfo(
        call_id=call_id,
        appointment_date=appointment_date,
    )
    db.session.add(call)
    db.session.commit()

    print("Rendez-vous enregistré : " + str(repr(call)))
    return jsonify({"status": "received", "appointment_date": appointment_date}), 200


if __name__ == "__main__":
    app.run(debug=True)