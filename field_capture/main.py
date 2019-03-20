
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, get_flashed_messages
)
from .db import get_db
from .room import room_bp

bp = Blueprint('main', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    rooms = db.execute('select * from room where room_type=0').fetchall()
    if request.method == 'POST':
        if 'username' in request.form.keys():
            session.clear()
            if request.form['username'] == '':
                flash('Write correct username')
                return redirect(url_for('main.index'))
            session['username'] = request.form['username']
        elif 'room_name' in request.form.keys():
            return redirect(url_for('room.create'), code=307)
        elif 'room_code' in request.form.keys():
            return redirect(url_for('room.room', room_id=request.form['room_code']), code=307)
    return render_template('index.html', rooms=rooms)

