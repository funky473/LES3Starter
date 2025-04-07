from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)

  def __init__(self, username, password):
    self.username= username
    self.set_password(password)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)
    
class Student(db.Model):
  id = db.Column(db.String(9), primary_key=True)
  first_name = db.Column(db.String(120), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
  image = db.Column(db.String(120), nullable=False)
  programme = db.Column(db.String(120), nullable=False)
  start_year = db.Column(db.Integer, nullable=False)
  courses = db.relationship('Course', secondary='student_course', backref='students')




  
class Course(db.Model):
  code = db.Column(db.String(9), primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  #students = db.relationship('Student', secondary='student_course', backref='courses')



class StudentCourse(db.Model):
  __tablename__ = 'student_course'
  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.String(9), db.ForeignKey('student.id'))
  course_code = db.Column(db.String(9), db.ForeignKey('course.code'))
  


