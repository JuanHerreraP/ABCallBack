from flask import Flask, request, jsonify
import pika
from flask_cors import CORS
import json

app = Flask(__name__)

RABBITMQ_HOST = 'localhost'
queues = ['pqr','pqrBackup']
QUEUE_NAME = queues[1]
cors = CORS(app)

def send_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_publish(exchange='',
                        routing_key=QUEUE_NAME,
                        body=json.dumps(message))
    print(" PQR enviado a la cola de mensajes ")
    connection.close()

@app.route('/pqrs', methods=['POST'])
def send_message():
    message = {"nombre":request.json['nombre'],
               "email":request.json['email'],
               "asunto":request.json['asunto'],
               "peticion":request.json['peticion']}
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        send_to_queue(message)
        return jsonify({'success': 'Message sent to RabbitMQ'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)