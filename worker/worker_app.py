import os
import redis
from dotenv import load_dotenv


def fib(index):
    if index < 2: return 1
    return fib(index - 1) + fib(index - 2)

def message_handler(msg):
    """Handle messages from Redis pub/sub"""
    if msg['type'] == 'message':
        value = msg['data']
        try:
            index = int(value)
            result = fib(index)
            redis_client.hset('values', value, result)
            print(f"Calculated fib({index}) = {result}")
        except ValueError: print(f"Received invalid index: {value}")


load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_client = redis.Redis(host = REDIS_HOST, port=REDIS_PORT, decode_responses=True)
pubsub = redis_client.pubsub()
pubsub.subscribe('insert')

if __name__ == '__main__':
    print('<<< Worker started >>>')
    for message in pubsub.listen(): message_handler(message)

