from flask import Flask, render_template, redirect, request, session, flash
from datetime import datetime
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
import requests

app = Flask(__name__)
app.secret_key = ('kerbz')
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def login_landing():
    return render_template('loginlanding.html')

@app.route('/registration')
def registration():
    return render_template('registrationlanding.html')

@app.route('/login', methods=['POST'])
def login_user():
    is_vaild = True

    if not request.form['em']:
        is_valid = False
        flash('Enter an email to log in')
        return redirect('/')
    
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash('Enter a valid email')
        return redirect('/')

@app.route('/register', methods=['POST'])
def register_user():
    is_valid = True

    if len(request.form['fn']) < 2:
        is_valid = False

        flash('First name must be at least 2 characters long.')
    if len(request.form['ln']) < 2:
        is_valid = False

        flash('Last name must be at least 2 characters long')
    if len(request.form['pw']) < 8:
        is_valid = False

        flash('Password must be atleast 8 characters long')
    if request.form['pw'] != request.form['c_pw']:
        is_valid = False

        flash('Passwords must match.')
    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash('Please use valid email.')
    
    if is_valid:
        encrypted_pw = bcrypt.generate_password_hash(request.form['pw'])

        mysql = connectToMySQL('mydb')
        query = 'INSERT INTO users (firstName, lastName, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW())'
        data = {
            'fn': request.form['fn'],
            'ln': request.form['ln'],
            'em': request.form['em'],
            'pw': encrypted_pw
        }
        session['user_id'] = mysql.query_db(query, data)
        return redirect('/quiz')
    else:
        flash('ERROR - Try again', 'error')
        return redirect('/')
    
@app.route('/quiz')
def quiz_landing():
    return render_template('housequiz.html')

# For when the answers are actually stored in the database and the house is dependent on answers
# @app.route('/quizsubmit', methods=['POST'])

@app.route('/house', methods=['POST', 'GET'])
def house_results():
    house = requests.get('https://www.potterapi.com/v1/sortingHat').content.decode().replace('"', '')
    return render_template('house_results.html', house=house)




if __name__ == '__main__':
    app.run(debug=True)