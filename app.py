from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/D/учеба/Flask/Flask_sait/instance/people.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/D/учеба/Flask/Flask_sait/instance/stud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


class Students(db.Model):
    id_student = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_game = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(100), nullable=False)
    href = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Students %r>' % self.id_student


class Students_web(db.Model):
    id_student = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    studies = db.Column(db.Text, nullable=False)
    programm = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Students_web %r>' % self.id_student


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/kurs3')
def kurs3():
    return render_template("3kurs.html")


@app.route('/kurs4/', methods=['POST', 'GET'])
def kurs4():
    students = Students.query.order_by(Students.id_student.asc()).all()
    return render_template("4kurs.html", students=students)


@app.route('/kurs4/<int:id>')
def students_web(id_student):
    student = Students_web.query.get(id_student)
    return render_template("students_web.html", student=student)


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
