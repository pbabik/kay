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
    emit('joined',{'nick':data['nick']}, room=mapid)

@socketio.on('leave')
def on_leave(data):
    username = data['nick']
    mapid = data['map']
    leave_room(mapid)
    emit('left',{'nick':data['nick']}, room=mapid)

@socketio.on('ping_request')
def on_ping(data):
    emit('ping',room=data['map'])

@socketio.on('send_chat')
def on_chat(data):
    emit('chat',{'nick':data['nick'],'msg':data['msg']},room=data['map'])

@socketio.on('move')
def handle_user_move(data):
    x = data['x']
    y = data['y']
    color = data['color']
    nick = data['nick']
    mapid = data['map']
    emit('usermove',{'x':x,'y':y,'nick':nick,'color':color},room=mapid)

@socketio.on('lost_gps')
def handle_user_lost(data):
    nick = data['nick']
    mapid = data['map']
    emit('userlost',{'nick':nick},room=mapid)

@socketio.on('pause')
def handle_user_pause(data):
    nick = data['nick']
    mapid = data['map']
    emit('userpaused',{'nick':nick},room=mapid)

@socketio.on('play')
def handle_user_play(data):
    nick = data['nick']
    mapid = data['map']
    emit('userplayed',{'nick':nick},room=mapid)

if __name__ == '__main__':
    socketio.run(app)
