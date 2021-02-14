import time
from datetime import datetime

import requests


def print_message(message):
    t = message['time']
    dt = datetime.fromtimestamp(t)
    dt = dt.strftime('%H:%M:%S')
    print(dt, message['name'])
    print(message['text'])
    print()


after = 0
name = 'Имя'

while True:
    response = requests.get(
        'http://127.0.0.1:5000/messages',
        params={'after': after, 'name': name}
    )
    messages = response.json()['messages']
    for message in messages:
        print_message(message)
        after = message['time']

    response = requests.get(
        'http://127.0.0.1:5000/status',
        params={'after': after, 'name': name}
    )
    messages = response.json()
    print(messages)
    
    # response = requests.get(
    #     'http://127.0.0.1:5000/rooms',
    #     params={'after': after, 'name': name}
    # )
    # rooms = response.json() 
    # for room in rooms:
    #     print(room['name'])

    time.sleep(1)