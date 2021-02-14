import time
import json
import random
import atexit
import requests
from datetime import datetime
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
db = [
    {
        'time': time.time(),
        'name': 'Система',
        'text': 'Приветствуем всех в нашем чате!',
        'room': 'main',
    },
]
rooms = [
    {
        'name': 'main',
        'desc': 'Основная комната',
    },
]

predictions = ['бесспорно', 'предрешено', 'никаких сомнений', 'определенно да', 'Можешь быть уверен в этом',
'Мне кажеться да', 'вероятнее всего', 'Хорошие перспективы', 'знаки говорят да', 'ДА', 'пока не ясно', 'пробуй снова',
'спроси позже', 'Лучше не рассказывать', 'Сейчас нельзя предсказать', 'Сконцентрируйся и спроси опять', 'Даже не думай',
'Мой ответ НЕТ', 'по моим данным НЕТ', 'Перспетивы не очень хорошие', 'Весьма сомнительно']


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/status")
def status():
    dt_now = datetime.now()
    userList = []
    for msg in db:
        userList.append(msg['name'])

    return {
        'status': True,
        'name': 'Messenger',
        'users': len(set(userList)),
        'msgs' : len(db),
        'time1': time.asctime(),
        'time2': time.time(),
        'time3': dt_now,
        'time4': str(dt_now),
        'time5': dt_now.strftime('%Y/%m/%d time: %H:%M:%S'),
        'time6': dt_now.isoformat()
    }

@app.route("/rooms")
def get_rooms():
    dt_now = datetime.now()
    return json.dumps(rooms)

@app.route("/send", methods=['POST'])
def send_message():
    data = request.json

    if not isinstance(data, dict):
        return abort(400)
    # if set(data.keys()) != {'name', 'text'}:
    #     return abort(400)
    if 'name' not in data or 'text' not in data:
        return abort(400)
    if len(data) > 4:
        return abort(400)

    name = data['name']
    text = data['text']
    try:
        room = data['room']
    except:
        room = 'main'

    if not isinstance(name, str) or \
            not isinstance(text, str) or \
            name == '' or \
            text == '':
        return abort(400)


    message = {
        'time': time.time(),
        'name': name,
        'text': text,
        'room': room,
    }

    if text.find('/help') == 0:
        new_text = '/help - показать команды \n\r' + '/private [name] [msg] написать приватное сообщение \n\r' + '/room [name] написать сообщение в комнату [name] \n\r' + '/createroom [name] [desc] созданть комнату [name] и дать ей описание [desc] \n\r' + '/8ball получить предсказание от шара судьбы \n\r'
        message.update({'text': new_text, 'for': name})

    if text.find('/private') == 0:
        text.replace('  ', ' ')
        array = text.split(' ',2);
        forname = array[1]
        new_text = array[2]
        message.update({'text': new_text, 'for': forname})
        
    if text.find('/8ball') == 0:
        new_text = predictions[random.randint(0, 19)]
        message.update({'name':'шар судьбы', 'text': new_text, 'for': name})

    if text.find('/room') == 0:
        text.replace('  ', ' ')
        array = text.split(' ',2);
        room = array[1]
        new_text = array[2]
        message.update({'text': new_text, 'room': room})

    if text.find('/createroom') == 0:
        text.replace('  ', ' ')
        array = text.split(' ',2);
        new_room = array[1]
        description = array[2]

        room_exist = False 
        for room in rooms:
            if room['name'] == new_room:
                room_exist = True                
        
        if room_exist:
            new_text = 'Такая комната уже существует, для перехода в неё используейте команду /room имяКомнаты'
            message.update({'name':'система', 'text': new_text,  'for': name})

        else:
            new_text = 'Пользователь ' + name + ' создал комнату ' + new_room
            message.update({'name':'система', 'text': new_text})
            rooms.append({'name': new_room, 'desc': description})

    db.append(message)

    return {'ok': True}


@app.route("/messages")
def get_messages():
    """messages from db after given timestamp"""
    try:
        after = float(request.args['after'])
    except:
        return abort(400)

    try:
        room = request.args['room']
    except:
        room = 'main'
    try:
        name = request.args['name']
    except:
        name = 'Гость'
        
    result = []
    for message in db:

        if message['time'] > after and message['room'] == room and message.get('for') == None:
            result.append(message)

        if message['time'] > after and message.get('for') == name:
            result.append(message)

        if len(result) >= 100:
            break

    return {'messages': result}



def check_silent():
    i = -1
    while db[i]['room'] != 'main':
        i -= 1
    lastMsg = db[i]['time']
    if time.time() - 60 > lastMsg: # больше минуты от последнего сообщения
        r = requests.get('https://api.forismatic.com/api/1.0/?method=getQuote&format=jsonp&jsonp=parseQuote')
        quoteStr = r.text.replace('parseQuote(', '')
        quoteStr = quoteStr.replace(')', '')
        quote = json.loads(quoteStr)
        text = quote['quoteText']
        name = quote['quoteAuthor']
        if name == '':
            name = 'Шальная мысль'
        message = {
            'time': time.time(),
            'name': name,
            'text': text,
            'room': 'main',
        }
        db.append(message)

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_silent, trigger="interval", seconds=3)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    app.run()
