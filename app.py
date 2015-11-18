#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from flask import Flask, render_template, request, abort, make_response, g
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['nick']
    mapid = data['map']
    join_room(mapid)
    send(username + ' has entered the room.', room=mapid)

@socketio.on('leave')
def on_leave(data):
    username = data['nick']
    mapid = data['map']
    leave_room(mapid)
    send(nick + ' has left the room.', room=mapid)

@socketio.on('move')
def handle_user_move(data):
    x = data['x']
    y = data['y']
    color = data['color']
    nick = data['nick']
    mapid = data['map']
    emit('usermove',{'x':x,'y':y,'nick':nick,'color':color},room=mapid)


if __name__ == '__main__':
    socketio.run(app)
