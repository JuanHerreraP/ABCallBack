from flask import Flask, request, jsonify
import pika
from flask_cors import CORS
import json
import uuid

app = Flask(__name__)

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'pqr'
STATUS_QUEUE_NAME = 'pqr_status'
cors = CORS(app)

def send_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_publish(exchange='',
                          routing_key=QUEUE_NAME,
                          body=json.dumps(message))
    print("PQR enviado a la cola de mensajes")
    connection.close()

def get_status_from_queue(pqr_id):
    print("CHECKING STATUS FOR PQR OF ID: ", pqr_id)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=STATUS_QUEUE_NAME)
    
    status = None
    
    def callback(ch, method, properties, body):
        nonlocal status
        message = body.decode()
        status_message = json.loads(message)
        if status_message["id"] == pqr_id:
            status = status_message["status"]
            ch.stop_consuming()  # Stop consuming messages once the desired one is found
    
    channel.basic_consume(queue=STATUS_QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    try:
        channel.start_consuming()
    except Exception as e:
        print(f"An error occurred: {e}")

    connection.close()
    
    if status:
        return status
    else:
        return None


@app.route('/pqrs', methods=['POST'])
def send_message():
    # Assign a unique ID to each PQR
    message = {
        "id": str(uuid.uuid4()),  # Unique ID
        "nombre": request.json['nombre'],
        "email": request.json['email'],
        "asunto": request.json['asunto'],
        "peticion": request.json['peticion']
    }

    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        send_to_queue(message)
        return jsonify({'success': 'Message sent to RabbitMQ', 'id': message['id']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/check-status/<string:pqr_id>', methods=['GET'])
def check_status(pqr_id):
    print(f"Received request for PQR ID: {pqr_id}")
    status = get_status_from_queue(pqr_id)
    print(f"Status found: {status}")
    if status:
        return jsonify(status=status), 200
    else:
        return jsonify(status="not_found"), 404

if __name__ == '__main__':
    app.run(port=5001)
