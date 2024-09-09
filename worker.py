import pika
import json

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'pqr'
STATUS_QUEUE_NAME = 'pqr_status'

def send_status_update(pqr_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=STATUS_QUEUE_NAME)
    status_message = {"id": pqr_id, "status": "processed"}
    channel.basic_publish(exchange='',
                          routing_key=STATUS_QUEUE_NAME,
                          body=json.dumps(status_message))
    connection.close()

def callback(ch, method, properties, body):
    message = body.decode()
    message_data = json.loads(message)
    print(f" [x] Recibido: {message_data}")

    # Send status update to the status queue
    send_status_update(message_data['id'])

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print(" [*] Esperando mensajes. Para salir presiona CTRL+C")
channel.start_consuming()
