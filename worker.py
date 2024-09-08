import pika
import requests
import json

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'pqr'
FLASK_API_URL = 'http://127.0.0.1:5000/receive_message' 

def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Recibido: {json.loads(message)}")
    
    # Enviar el mensaje a la aplicación Flask
    try:
        response = requests.post(FLASK_API_URL, json=json.dumps(message))
        if response.status_code == 200:
            print(f" [x] Mensaje enviado a Flask: {message}")
        else:
            print(f" [!] Error enviando el mensaje a Flask: {response.status_code}")
    except Exception as e:
        print(f" [!] Excepción al enviar el mensaje a Flask: {e}")

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print(" [*] Esperando mensajes. Para salir presiona CTRL+C")
channel.start_consuming()