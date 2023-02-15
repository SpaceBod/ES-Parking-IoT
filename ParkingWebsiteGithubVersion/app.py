from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
import database
import os
import parking
from PIL import Image, ImageDraw, ImageFont
app = Flask(__name__)


app.secret_key = 'secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index():
    data()
    stats = database.getstats()
    return render_template('table.html', title='Parking', stats = stats)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/favicon.ico')

@app.route('/api/data')
def data():
    return {"data": database.getallspaces()}

@app.route('/map')
def map():
    parking_spots = database.parkinggen()
    img = parking.draw_parking_spots(parking_spots, 6, 16, 80, 160)
    img.save(os.path.join(app.root_path, 'static/Parking.png'), format="JPEG", subsampling=0, quality=100)

    return render_template('map.html', title='Map')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        user, info, plate = database.userlogin(username,password)
        if user:
            session['loggedin'] = True
            session['userid'] = username
            message = 'Logged in successfully !'
            loclist = ['Exit', 'Car Park Entrance', 'Car Park Exit']
            typelist = ["Normal", "Disabled", "Electric"]

            return render_template('user.html', message = message, data=info, loclist=loclist, typelist=typelist, plate=plate)
        else:
            message = 'Incorrect username/password'

    return render_template('login.html', message = message)


@app.route('/updatepref', methods=['POST'])
def updatepref():
    pref = request.form.get('pref')
    name = request.form.get('id')
    rfid = database.getrfid(name)
    database.updatepref(str(rfid), str(pref))
    session.modified = True
    return render_template('empty.html')

@app.route('/updatetype', methods=['POST'])
def updatetype():
    type = request.form.get('type')
    name = request.form.get('id')
    rfid = database.getrfid(name)
    database.updatetype(str(rfid), str(type))
    session.modified = True
    return render_template('empty.html')

@app.route('/addplate', methods=['POST'])
def addplate():
    plate = request.form.get('plateno')
    name = request.form.get('id')
    print(plate,name)
    database.addplate(plate, name)

    return render_template('empty.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        card = request.form['card']
        add = database.adduser(username, password, card)
        message = 'Registration Successful!'

    return render_template('register.html', message = message)

@app.route('/empty')
def empty():
    return render_template('empty.html')


@app.after_request
def add_header(response):
    response.cache_control.max_age = 30
    return response



if __name__ == '__main__':
    app.run()

