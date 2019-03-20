import functools

from flask import (
        Blueprint, flash, g, request, render_template, session, redirect, url_for, abort
)
import uuid

from .db import get_db
from .errors import my_custom_error

room_bp = Blueprint('room', __name__, url_prefix='/room')

def login_required(view):
    @functools.wraps(view)
    def wrapper(**kwargs):
        if 'username' not in session:
            flash('You must have username do play')
            return redirect(url_for('main.index')) 
        return view(**kwargs)
    return wrapper

@room_bp.route('/<room_id>', methods=['GET', 'POST'])
@login_required
def room(room_id):
    db = get_db()
    current_room = db.execute('select * from room where id=?', (room_id,)).fetchone()
    if session.get('room_id') is not None and session.get('room_id') != current_room['room_id']:
        return my_custom_error('errors/error.html', message='you in other room now')
    elif session.get('room_id') is not None and session.get('room_id') == current_room['room_id']:
        return render_template('room.html', db_data=current_room)
    if current_room is None:
        return abort(404)
    if int(current_room['free_place']) <= 0:
        return my_custom_error('errors/room_place_error.html', message='room is full')
    if current_room['playing'] == '1':
        return my_custom_error('errors/room_playing_error.html', message='players already plays')
    #add room_id to user session
    session['room_id'] = room_id
    #Increase a number of players
    db.execute('UPDATE room SET free_place=? where id=?', (int(current_room['free_place'])-1, room_id))
    db.commit()
    current_room = db.execute('select * from room where id=?', (room_id,)).fetchone()
    return render_template('room.html', db_data=current_room) 

@room_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    #create and prepare room to play
    #create room record in data base
    if request.form['room_name'] == '':
        flash('Wirte a correct room name')
        return redirect(url_for('main.index'))
    db = get_db()
    room_type = False
    room_size = int(request.form['room_size'])
    if request.form['room_type'] == 'pub':
        room_type = False
    elif request.form['room_type'] == 'priv':
        room_type = True
    room_id = uuid.uuid4().hex
    db.execute('INSERT INTO room (id, room_name, room_size, room_type, free_place, playing) VALUES (?, ?, ?, ?, ?, ?)', (room_id, request.form['room_name'], room_size, room_type, room_size, False))
    db.commit()
    # add a player, which create room to the room
    return redirect(url_for('.room', room_id=room_id))

@room_bp.route('/exit', methods=['GET', 'POST'])
@login_required
def exit_r():
    if 'room_id' not in session:
        abort(404)
    db = get_db()
    room_free_place = db.execute('select free_place, room_size from room where id=?', (session['room_id'],)).fetchone()
    if int(room_free_place['free_place']) == int(room_free_place['room_size'])-1:
        db.execute('delete from room where id=?', (session['room_id'],))
    else:
        db.execute('update room set free_place=? where id=?', (int(room_free_place['free_place'])+1, session['room_id']))
    db.commit()
    session.pop('room_id')
    return redirect(url_for('main.index'))
