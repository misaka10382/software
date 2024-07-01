from flask import request, jsonify, Blueprint, render_template, url_for, session, redirect
from models import db, User, bcrypt, Doctor, DoctorAvailability, Admin, Registration
from datetime import datetime


doctors = Blueprint('doctors', __name__)

@doctors.route('/dashboard')
def doctor_dashboard():
    if 'user_id' not in session :
        return redirect(url_for('auth.login'))
    doctor_id = session['user_id']
    doctor = Doctor.query.get(doctor_id)
    return render_template('doctor_dashboard.html', doctor=doctor)

@doctors.route('/update_info', methods=['GET', 'POST'])
def update_doctor_info():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    doctor_id = session['user_id']
    doctor = Doctor.query.get(doctor_id)
    if request.method == 'POST':
        doctor.introduction = request.form['introduction']
        doctor.pay = float(request.form['pay'])
        db.session.commit()
        return redirect(url_for('doctors.doctor_dashboard'))
    return render_template('update_doctor_info.html', doctor=doctor)

@doctors.route('/view_registrations')
def view_doctor_registrations():
    if 'user_id' not in session :
        return redirect(url_for('auth.login'))
    doctor_id = session['user_id']
    doctor = Doctor.query.get(doctor_id)
    registrations = Registration.query.filter_by(doctor_name=doctor.username).all()
    return render_template('view_doctor_registrations.html', registrations=registrations)

@doctors.route('/delete_registration/<int:registration_id>', methods=['POST'])
def delete_doctor_registration(registration_id):
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
    return redirect(url_for('doctors.view_doctor_registrations'))

@doctors.route('/set_availability', methods=['GET', 'POST'])
def set_doctor_availability():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    doctor_id = session['user_id']
    doctor = Doctor.query.get(doctor_id)

    if request.method == 'POST':
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date).first()

        if availability:
            for hour in ['8_9', '9_10', '10_11', '11_12', '12_13', '13_14', '14_15', '15_16']:
                time_slot = hour.replace('_', '-')
                registration_exists = Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot=time_slot).first()
                if not registration_exists:
                    available = request.form.get(f'available_{hour}') == 'on'
                    setattr(availability, f'hour_{hour}', available)
            db.session.commit()
        return redirect(url_for('doctors.set_doctor_availability', date=date_str))

    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, date=date).first()

    time_slots = {
        '8_9': availability.hour_8_9 if availability else False,
        '9_10': availability.hour_9_10 if availability else False,
        '10_11': availability.hour_10_11 if availability else False,
        '11_12': availability.hour_11_12 if availability else False,
        '12_13': availability.hour_12_13 if availability else False,
        '13_14': availability.hour_13_14 if availability else False,
        '14_15': availability.hour_14_15 if availability else False,
        '15_16': availability.hour_15_16 if availability else False
    }

    registrations = {
        '8-9': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='8-9').first(),
        '9-10': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='9-10').first(),
        '10-11': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='10-11').first(),
        '11-12': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='11-12').first(),
        '12-13': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='12-13').first(),
        '13-14': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='13-14').first(),
        '14-15': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='14-15').first(),
        '15-16': Registration.query.filter_by(doctor_name=doctor.username, date=date, time_slot='15-16').first()
    }

    return render_template('set_doctor_availability.html', doctor=doctor, time_slots=time_slots, registrations=registrations, date=date)
