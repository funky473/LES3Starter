from App.models import User, Student, Course, StudentCourse
import click, csv
from flask import Flask
from flask.cli import with_appcontext
from App import app, initialize_db


@app.cli.command("init")
def initialize():
  initialize_db()

@app.cli.command("get_students")
def get_students():
  Students = StudentCourse.query.all()
  for student in Students:
    print(student.student_id, student.course_code)
