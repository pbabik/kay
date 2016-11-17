#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import os
from flask import Flask, url_for, redirect, render_template, request, abort, make_response, g, send_file, send_from_directory, jsonify
from werkzeug import secure_filename
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

@app.route('/filez/<filename>')
def download(filename):
    UPLOAD_FOLDER = 'uploads'
    if request.args.get('thumb'):
        if os.path.exists(os.path.join(UPLOAD_FOLDER, 'mini_'+filename)):
            return send_from_directory(UPLOAD_FOLDER,'mini_'+filename)
        else:
            im = Image.open(os.path.join(UPLOAD_FOLDER, filename))
            im.thumbnail((400,400), Image.ANTIALIAS)
            im.save(os.path.join(UPLOAD_FOLDER,'mini_'+filename))
            return send_from_directory(UPLOAD_FOLDER,'mini_'+filename)
    else:
        return send_from_directory('uploads',filename)

@app.route('/upload',methods=['POST'])
def upload():
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    the_file = request.files['file']
    if the_file:
        filename = secure_filename(the_file.filename)
        the_file.save(os.path.join('uploads', filename))
        im = Image.open(os.path.join('uploads', filename))
        im.thumbnail((1280,1280), Image.ANTIALIAS)
        im.save(os.path.join('uploads', filename))
        return jsonify({"uploaded":filename})
    else:
        abort(400)

@app.route('/map/<mapid>')
def direct_link(mapid):
    return redirect(url_for('index')+'#'+mapid)

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

@socketio.on('send_photo')
def on_photo(data):
    emit('photo',{'nick':data['nick'],'file':data['file']},room=data['map'])

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
    socketio.run(app,host='0.0.0.0')
