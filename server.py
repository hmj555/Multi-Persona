from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# 데이터 저장 (페르소나 생성)
@app.route("/api/persona", methods=["POST"])
def create_persona():
    data = request.json
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO personas (age, gender, mbti, roles) VALUES (?, ?, ?, ?)",
              (data["age"], data["gender"], data["mbti"], ",".join(data["roles"])))
    conn.commit()
    conn.close()
    return jsonify({"message": "Persona saved!"})

if __name__ == "__main__":
    app.run(debug=True)