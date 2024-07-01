from flask import request, jsonify, Blueprint, render_template, url_for, session, redirect
from models import db, User, bcrypt, Doctor, DoctorAvailability, Admin, Registration
from datetime import datetime

users = Blueprint('users', __name__)

@users.route('/users')
def display_users():
    users = User.query.all()
    doctors = Doctor.query.all()
    doctors_available = DoctorAvailability.query.all()
    return render_template('users.html', users=users, doctors=doctors, doctors_available=doctors_available)

@users.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('user_dashboard.html', user=user)

@users.route('/view_registrations')
def view_registrations():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    registrations = Registration.query.filter_by(user_id=user_id).all()
    return render_template('view_registrations.html', registrations=registrations)

@users.route('/delete_registration/<int:registration_id>', methods=['POST'])
def delete_registration(registration_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    registration = Registration.query.get(registration_id)
    if registration:
        doctor = Doctor.query.filter_by(username=registration.doctor_name).first()
        if doctor:
            availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=registration.date).first()
            if availability:
                setattr(availability, f'hour_{registration.time_slot.replace("-", "_")}', True)
            db.session.delete(registration)
            db.session.commit()
    return redirect(url_for('users.view_registrations'))

@users.route('/select_department', methods=['GET', 'POST'])
def select_department():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    if request.method == 'POST':
        department = request.form['department']
        date_str = request.form['date']
        time_slot = request.form['time_slot']
        
        # 将日期字符串转换为 date 对象
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 查询符合条件的医生和他们的预约状态
        doctors = Doctor.query.filter_by(department=department).all()
        available_doctors = []
        for doctor in doctors:
            availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=date).first()
            if availability:
                available = getattr(availability, f'hour_{time_slot.replace("-", "_")}')
                available_doctors.append({
                    'id': doctor.id,
                    'username': doctor.username,
                    'department': doctor.department,
                    'available': available
                })
        return render_template('department_doctors.html', doctors=available_doctors, date=date_str, time_slot=time_slot, user_id=user_id)
    departments = db.session.query(Doctor.department).distinct().all()
    return render_template('select_department.html',departments=departments)

@users.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    doctor_id = request.form['doctor_id']
    date_str = request.form['date']
    time_slot = request.form['time_slot']

    # 将日期字符串转换为 date 对象
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # 创建挂号记录
    doctor = Doctor.query.get(doctor_id)
    new_registration = Registration(
        user_id=user_id,
        doctor_name=doctor.username,
        department=doctor.department,
        date=date,
        time_slot=time_slot
    )
    db.session.add(new_registration)

    # 更新医生的预约状态
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date).first()
    setattr(availability, f'hour_{time_slot.replace("-", "_")}', False)
    db.session.commit()

    return redirect(url_for('users.view_registrations'))

@users.route('/doctor_info/<int:id>', methods=['GET', 'POST'])
def doctor_info(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    doctor = Doctor.query.get(id)
    if request.method == 'POST':
        date = request.form['date']
        availability = DoctorAvailability.query.filter_by(doctor_id=id, date=date).first()
        return render_template('doctor_info.html', doctor=doctor, availability=availability, user_id=user_id)
    return render_template('doctor_info.html', doctor=doctor, user_id=user_id)


@users.route('/pay_fees', methods=['GET', 'POST'])
def pay_fees():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    if request.method == 'POST':
        # 获取所有未缴费的挂号信息
        registrations = Registration.query.filter_by(user_id=user_id, is_charge=False).all()
        for registration in registrations:
            registration.is_charge = True
        db.session.commit()
        return jsonify({'message': '缴费成功'}), 200

    registrations = Registration.query.filter_by(user_id=user_id, is_charge=False).all()
    total_fee = 0
    registration_details = []
    for registration in registrations:
        doctor = Doctor.query.filter_by(username=registration.doctor_name).first()
        if doctor:
            fee = doctor.pay
            total_fee += fee
            registration_details.append({
                'registration': registration,
                'fee': fee
            })
    return render_template('pay_fees.html', registration_details=registration_details, total_fee=total_fee)
