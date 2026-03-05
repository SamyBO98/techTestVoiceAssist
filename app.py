from flask import Flask, request, jsonify


app = Flask(__name__)

# Endpoint POST minimal pour /end-of-call
@app.route("/end-of-call", methods=["POST"])
def end_of_call():
    #Return 200 just to start
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True)