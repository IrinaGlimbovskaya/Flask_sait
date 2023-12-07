from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash


from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/D/учеба/Flask/Flask_sait/instance/sait.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'test'  # Указываем страницу входа


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Students %r>' % self.id_student


class studweb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    studies = db.Column(db.Text, nullable=False)
    programm = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)


class BullCowLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))


admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin_bp = Blueprint('MyAdmin', __name__, url_prefix='/admin')
admin.init_app(admin_bp)
app.register_blueprint(admin_bp)

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/test')
@auth.login_required
def test():
    return redirect(url_for('admin.index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        session.clear()
        app.logger.debug('User logged out successfully')
    else:
        app.logger.debug('User is not authenticated')
    return redirect(url_for('test'))


def generate_secret_number():
    # Генерируем случайное число из четырех цифр
    first_digit = random.randint(1, 9)  # Генерируем первую цифру от 1 до 9
    rest_of_digits = ''.join([str(random.randint(0, 9)) for _ in range(3)])  # Генерируем остальные три цифры
    secret_number = str(first_digit) + rest_of_digits
    return secret_number


@app.route('/')
@app.route('/home')
def index():
    students = Students.query.order_by(Students.id.asc()).all()
    return render_template("index.html")


# @app.route('/kurs<int:id_student>')
# def kurs3():
# return render_template("3kurs.html")


@app.route('/kurs<int:id>', methods=['POST', 'GET'])
def kurs_page(id):
    courses = Courses.query.order_by(Courses.id.asc()).all()  # по id вывести группу
    course = Courses.query.filter_by(id=id).first()
    students = Students.query.order_by(Students.id.asc()).all()
    print(id)
    # Извлекаем значения поля Name из объектов Courses
    names = [course.name for course in courses]

    print(names)
    return render_template("kurs_page.html", students=students, course=course)


@app.route('/students_web/<int:id>')
def students_web(id):
    try:
        student = db.session.query(studweb).filter_by(id=id).one()
        programm_sentences = re.findall(r'([А-ЯA-Z].*?[.!?])', student.programm)
        studies_sentences = re.findall(r'([А-ЯA-Z].*?[.!?])', student.studies)

        print("Programm Sentences:", programm_sentences)
        print("Studies Sentences:", studies_sentences)

        return render_template("students_web.html", student=student, programm_sentences=programm_sentences,
                               studies_sentences=studies_sentences)
    except NoResultFound:
        # Handle the case where the student with the given id is not found.
        # You can return an error page or a 404 Not Found response.
        return render_template("student_not_found.html")


@app.route('/bull_cow_log', methods=['GET', 'POST'])
def bull_cow_log():
    if request.method == 'POST':
        player_name = request.form.get('playerName')
        number = request.form.get('guessNumber')
        secret_number = generate_secret_number()
        session['secret_number'] = secret_number

        return redirect(url_for('bull_cow', player_name=player_name, number=number))
    return render_template('index_bull_cow.htm')


@app.route('/guess_num', methods=['GET', 'POST'])
def guess_num():
    if request.method == 'POST':
        player_name = request.form.get('playerName')
        number = request.form.get('guessNumber')
        secret_number = generate_secret_number()
        session['secret_number'] = secret_number
        new_record = BullCowLogin(player_name=player_name, number=number)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('bull_cow', player_name=player_name, number=number))
    return render_template('index_end.htm')


@app.route('/bull_cow/<player_name>/<number>', methods=['GET'])
def bull_cow(player_name, number):
    global attempts_count  # Объявляем, что мы будем использовать глобальный счетчик
    secret_number = session.get('secret_number')
    print(secret_number)
    bulls, cows = check_guess(number, secret_number)
    result = 'Вы победили!'
    if bulls == 4:  # Все цифры на своих местах
        new_record = BullCowLogin(player_name=player_name, number=number, result=result)
        db.session.add(new_record)
        db.session.commit()
        return render_template('bull_cow_congratulations.html', player_name=player_name)
    else:
        return render_template('bull_cow_try_again.html', player_name=player_name, number=number, bulls=bulls,
                               cows=cows)


def check_guess(guess, secret):
    bulls, cows = 0, 0
    for i in range(4):
        if guess[i] == secret[i]:
            bulls += 1
        elif guess[i] in secret:
            cows += 1
    return bulls, cows


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
