from models import db, User, Doctor, bcrypt,DoctorAvailability,Admin
from app import app
from datetime import datetime

with app.app_context():
    # 添加用户
    # user_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
    # test_user = User(username='testuser2', phone='1234567891', password=user_password)
    # db.session.add(test_user)

    # 添加医生
    # doctor_password = bcrypt.generate_password_hash('doctorpassword').decode('utf-8')
    # test_doctor = Doctor(username='doctorname', phone='1234567890',department='Cardiology', password=doctor_password)
    # db.session.add(test_doctor)
    # db.session.commit()

    admin = bcrypt.generate_password_hash('000000').decode('utf-8')
    admin_user = Admin(username='admin', password=admin)
    db.session.add(admin_user)
    db.session.commit()

    # 添加医生可预约时间


    # availibity = DoctorAvailability(doctor_id=test_doctor.id, date=datetime(2024, 6, 24),doctor_name=test_doctor.username,department=test_doctor.department
    #                                 )
    # db.session.add(availibity)
    # db.session.commit()
    print('已成功添加')
