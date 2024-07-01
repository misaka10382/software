from flask import request, jsonify, Blueprint,render_template,url_for,flash,redirect,session
from models import db, User, bcrypt,Doctor,DoctorAvailability,Admin,Registration
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin.route('/view_doctors')
def view_doctors():
    doctors = Doctor.query.all()
    return render_template('view_doctors.html',doctors=doctors)

@admin.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        department = request.form['department']
        pay = request.form['pay']
        introduction = request.form['introduction']
        new_doctor = Doctor(username=username, phone=phone, password=password, department=department, introduction=introduction,pay=pay)
        db.session.add(new_doctor)
        db.session.commit()
        
        # Create availability for the next week
        start_date = datetime.utcnow().date()
        for i in range(7):
            date = start_date + timedelta(days=i)
            availability = DoctorAvailability(doctor_id=new_doctor.id,doctor_name=new_doctor.username,department=new_doctor.department, date=date)
            db.session.add(availability)
        db.session.commit()
        
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('add_doctor.html')


@admin.route('/edit_doctor/<int:id>',methods=['GET','POST'])
def edit_doctor(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    doctor = Doctor.query.get(id)
    if request.method == 'POST':
        doctor.introduction = request.form['introduction']
        doctor.pay = float(request.form['pay'])
        db.session.commit()
        return redirect(url_for('admin.view_doctors'))
    return render_template('edit_doctor.html', doctor=doctor)

@admin.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # 删除这个医生相关的所有挂号信息
    registrations = Registration.query.filter_by(doctor_name=doctor.username).all()
    for registration in registrations:
        db.session.delete(registration)
    
    # 删除这个医生相关的所有预约状态信息
    availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    for availability in availabilities:
        db.session.delete(availability)
    
    # 删除医生本身
    db.session.delete(doctor)
    db.session.commit()
    
    flash('Doctor and all related information deleted successfully!', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin.route('/doctor/<int:id>', methods=['GET', 'POST'])
def view_doctor(id):
    doctor = Doctor.query.get(id)
    if request.method == 'POST':
        date = request.form['date']
        availability = DoctorAvailability.query.filter_by(doctor_id=id, date=date).first()
        return render_template('view_doctor.html', doctor=doctor, availability=availability)
    return render_template('view_doctor.html', doctor=doctor)


@admin.route('/view_patients')
def view_patients():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    patients = User.query.all()
    return render_template('view_patients.html', patients=patients)

@admin.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    patient = User.query.get(id)
    if request.method == 'POST':
        patient.username = request.form['username']
        patient.phone = request.form['phone']
        db.session.commit()
        flash('Patient information updated successfully!', 'success')
        return redirect(url_for('admin.view_patients'))
    return render_template('edit_patient.html', patient=patient)


@admin.route('/view_departments')
def view_departments():
    if 'user_id' not in session :
        return redirect(url_for('auth.login'))
    departments = db.session.query(Doctor.department).distinct().all()
    return render_template('view_departments.html', departments=departments)


@admin.route('/delete_department/<string:department>', methods=['POST'])
def delete_department(department):
    if 'user_id' not in session or session.get('user_type') != 'Admin':
        return redirect(url_for('admin.admin_login'))
    
    # 删除科室对应的所有挂号信息
    registrations = Registration.query.filter_by(department=department).all()
    for registration in registrations:
        db.session.delete(registration)
    
    # 删除科室对应的所有医生及其预约状态
    doctors = Doctor.query.filter_by(department=department).all()
    for doctor in doctors:
        availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        for availability in availabilities:
            db.session.delete(availability)
        db.session.delete(doctor)
    
    db.session.commit()
    flash('Department and all related information deleted successfully!', 'success')
    return redirect(url_for('admin.view_departments'))

