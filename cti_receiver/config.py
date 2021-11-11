import os

BROKER_HOST = os.environ.get('BROKER_HOST', '127.0.0.1')
BROKER_PORT = os.environ.get('BROKER_PORT', '5672')
BROKER_USER = os.environ.get('BROKER_USER', '')
BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', '')

MONGO_HOST = os.environ.get('MONGO_HOST', '127.0.0.1')
MONGO_PORT = os.environ.get('MONGO_PORT', '27017')
MONGO_USER = os.environ.get('MONGO_USER', '')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '')
