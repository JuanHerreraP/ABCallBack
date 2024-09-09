from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'abcall.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

class PQR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    email = db.Column(db.String(50))
    asunto = db.Column(db.String(50))
    peticion = db.Column(db.String(128))

messages = []

@app.route('/receive_message', methods=['POST'])
def receive_message():
    message = request.json
    print(message)
    message = json.loads(message)
    print(message)
    if message:
        """print(message["nombre"])
        nuevo_pqr = PQR(nombre=message["nombre"], email=message["email"], asunto=message["asunto"], peticion=message["peticion"])
        """
        print("PQR agregado en la base de datos")
        return jsonify({"status": "success", "message": "Mensaje recibido"}), 200
    else:
        return jsonify({"status": "error", "message": "No message provided"}), 400
    
if __name__ == '__main__':
    app.run(port=5002)