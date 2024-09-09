from flask import Flask, request, jsonify
import pika
import json

app = Flask(__name__)

RABBITMQ_HOST = 'localhost'




if __name__ == '__main__':
    app.run(port=5000)
