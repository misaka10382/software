from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(10),nullable=True,default="")
    age = db.Column(db.Integer,nullable=True,default=18)

    def __repr__(self):
        return f"User('{self.username}', '{self.phone}','{self.password}')"
    
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    introduction = db.Column(db.Text, nullable=True,default="")
    availability = db.relationship('DoctorAvailability', backref='doctor', cascade="all, delete-orphan", lazy=True)
    pay = db.Column(db.Integer, nullable=False,default=15)
    def __repr__(self) -> str:
        # 返回一个字符串，表示这个对象的当前状态
        return f"Doctor('{self.name}', '{self.department}')"
    


    
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self) -> str:
        return f"Admin('{self.username}')"
    
class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor_name = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.day)
    hour_8_9 = db.Column(db.Boolean, nullable=False, default=True)
    hour_9_10 = db.Column(db.Boolean, nullable=False, default=True)
    hour_10_11 = db.Column(db.Boolean, nullable=False, default=True)
    hour_11_12 = db.Column(db.Boolean, nullable=False, default=True)
    hour_12_13 = db.Column(db.Boolean, nullable=False, default=True)
    hour_13_14 = db.Column(db.Boolean, nullable=False, default=True)
    hour_14_15 = db.Column(db.Boolean, nullable=False, default=True)
    hour_15_16 = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"DoctorAvailability('{self.doctor_id}', '{self.date}')"

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g., "8:00-9:00"
    is_charge = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref=db.backref('registrations', lazy=True))

    def __repr__(self) -> str:
        return f"Registration('{self.user_id}', '{self.doctor_name}', '{self.department}', '{self.date}', '{self.time_slot}')"
    
# 创建数据库和表
with app.app_context():
    db.create_all()
