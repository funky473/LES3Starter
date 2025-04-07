import os, csv
from flask import Flask, redirect, render_template, jsonify, request, send_from_directory, flash, url_for
from sqlalchemy.exc import OperationalError, IntegrityError
from App.models import db, User, Student, Course, StudentCourse
from datetime import timedelta

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
    current_user,
)


def create_app():
  app = Flask(__name__, static_url_path='/static')
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'MySecretKey'
  app.config['PREFERRED_URL_SCHEME'] = 'https'
  app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
  app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
  app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
  app.config["JWT_COOKIE_SECURE"] = True
  app.config["JWT_SECRET_KEY"] = "super-secret"
  app.config["JWT_COOKIE_CSRF_PROTECT"] = False
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

  app.app_context().push()
  return app


app = create_app()
db.init_app(app)

jwt = JWTManager(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
  return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
  identity = jwt_data["sub"]
  return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
  flash("Your session has expired. Please log in again.")
  return redirect(url_for('login'))


def parse_students():
  with open('students.csv', mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
      student = Student(id=row['ID'],
                        first_name=row['FirstName'],
                        image=row['Picture'],
                        last_name=row['LastName'],
                        programme=row['Programme'],
                        start_year=row['YearStarted'])
      db.session.add(student)
    db.session.commit()

def create_users():
  rob = User(username="rob", password="robpass")
  bob = User(username="bob", password="bobpass")
  sally = User(username="sally", password="sallypass")
  pam = User(username="pam", password="pampass")
  chris = User(username="chris", password="chrispass")
  db.session.add_all([rob, bob])
  db.session.commit()


def create_courses():
  info1601 = Course(code="INFO1601", name="Intro To WWW Programming")
  info2602 = Course(code="INFO2602", name="Web Programming & Technologies 1")
  info1600 = Course(code="INFO1600", name="IT Concepts")
  comp2605 = Course(code="COMP2605", name="Database Management Systems")
  db.session.add_all([info1601, info2602, info1600, comp2605])
  db.session.commit()
def create_student_course():
  frist = StudentCourse(student_id="816035936", course_code="INFO1601")
  second = StudentCourse(student_id="816044364", course_code="INFO2602")
  db.session.add_all([frist , second])
  db.session.commit()

# uncomment after models are implemented
def initialize_db():
  db.drop_all()
  db.create_all()
  create_users()
  create_courses()
  parse_students()
  create_student_course()
  print('database intialized')


@app.route('/')
def login():
  return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_action():
  username = request.form.get('username')
  password = request.form.get('password')
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    response = redirect(url_for('home'))
    access_token = create_access_token(identity=user.id)
    set_access_cookies(response, access_token)
    return response
  else:
    flash('Invalid username or password')
    return redirect(url_for('login'))


@app.route('/app')
@app.route('/app/<code>')
@jwt_required()
def home(code="INFO1601"):
  # check if user is authenticated
  courses = Course.query.all()
  students = Student.query.all()
  enrolled_students = StudentCourse.query.filter_by(course_code=code).all()
  students_ids = [student.student_id for student in enrolled_students]
  enrolled = Student.query.filter(Student.id.in_(students_ids)).all()
  available_students = Student.query.filter(~Student.id.in_(students_ids)).all()
  course = Course.query.filter_by(code=code).first()
  return render_template('index.html', user=current_user, courses=courses, code=code, students=students,enrolled=enrolled,course=course, available_students=available_students)

@app.route('/add/<student>', methods=['POST'])
@jwt_required()
def add_student(student):
  student_id = request.form.get('student_id')
  course_code = request.form.get('course_code')
  student_course = StudentCourse(student_id=student_id, course_code=course_code)
  db.session.add(student_course)
  db.session.commit()
  return redirect(url_for('home', code=course_code))

@app.route('/remove/<student>', methods=['POST'])
@jwt_required()
def remove_student(student):
  course_code = request.form.get('course_code')
  student_course = StudentCourse.query.filter_by(student_id=student, course_code=course_code).first()
  db.session.delete(student_course)
  db.session.commit()
  return redirect(url_for('home', code=course_code))


@app.route('/logout')
def logout():
  response = redirect(url_for('login'))
  unset_jwt_cookies(response)
  flash('logged out')
  return response


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
