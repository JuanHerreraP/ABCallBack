from flask import Flask, request, jsonify
import pika
from flask_cors import CORS
import json
import pybreaker

app = Flask(__name__)

RABBITMQ_HOST = 'localhost'
PRIMARY_QUEUE = 'pqr'
BACKUP_QUEUE = 'pqrbk'
cors = CORS(app)

# Circuit Breaker con los tres estados
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,           # Número máximo de fallos antes de abrir el circuito
    reset_timeout=30      # Tiempo en segundos para pasar a medio abierto
)

# Función para enviar el mensaje a la cola adecuada
def send_to_queue(queue_name, message):
    if queue_name == PRIMARY_QUEUE:
        raise pybreaker.CircuitBreakerError("Error en la cola primaria")
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='',
                            routing_key=queue_name,
                            body=json.dumps(message))
        print(f" PQR enviado a la cola {queue_name}")
        connection.close()

# Función para hacer el cambio dinámico de la cola dependiendo del Circuit Breaker
@circuit_breaker
def send_message_with_circuit_breaker(message):
    try:
        print("Intentando usar la cola primaria")
        # Si el Circuit Breaker está cerrado o medio abierto, usa la cola primaria
        send_to_queue(PRIMARY_QUEUE, message)
        print("usa cola primaria")
    except pybreaker.CircuitBreakerError:
        print("Circuito abierto, usando la cola de respaldo")
        # Si el Circuit Breaker está abierto, cambia a la cola de respaldo
        send_to_queue(BACKUP_QUEUE, message)
    except Exception as e:
        print(f"Se produjo una excepción inesperada: {e}")

# Endpoint para recibir las peticiones de PQRS
@app.route('/pqrs', methods=['POST'])
def send_message():
    message = {
        "nombre": request.json['nombre'],
        "email": request.json['email'],
        "asunto": request.json['asunto'],
        "peticion": request.json['peticion']
    }
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        send_message_with_circuit_breaker(message)
        return jsonify({'success': 'Message sent to RabbitMQ'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
