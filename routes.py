from flask import request, jsonify, Blueprint,render_template,url_for,session,redirect
from models import db, User, bcrypt,Doctor,DoctorAvailability,Admin

auth = Blueprint('auth', __name__)



@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')

    if not username or not phone or not password:
        return jsonify({'message': '缺少必要的字段'}), 400

    user = User.query.filter((User.username == username) | (User.phone == phone)).first()
    if user:
        return jsonify({'message': '用户名或手机号已存在'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, phone=phone, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功'}), 201

@auth.route('/register',methods=['GET'])
def show_register():
    return render_template('register.html')

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')
    user_type = data.get('user_type')

    if not identifier or not password or not user_type:
        return jsonify({'message': '缺少必要的字段'}), 400

    if user_type == 'user':
        user = User.query.filter((User.username == identifier)).first()
    elif user_type == 'doctor':
        user = Doctor.query.filter(Doctor.username == identifier).first()
    elif user_type == 'Admin':
        user = Admin.query.filter(Admin.username == identifier).first()
    else:
        return jsonify({'message': '无效的用户类型'}), 400
    
    if user and bcrypt.check_password_hash(user.password, password):
        redirect_url = url_for('users.display_users')
        session['user_id'] = user.id
        if user_type == 'user':
            redirect_url = url_for('users.user_dashboard',user_id=user.id)
        elif user_type == 'doctor':
            redirect_url = url_for('doctors.doctor_dashboard',doctor_id=user.id)
        elif user_type == 'Admin':
            redirect_url = url_for('admin.admin_dashboard')
        return jsonify({'message': '登录成功', 'redirect_url': redirect_url,'id':user.id}), 200
    else:
        return jsonify({'message': '用户名/密码错误'}), 401
        
@auth.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')



@auth.route('/password_reset', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': '缺少必要的字段'}), 400

    user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({'message': '手机号未注册'}), 404

    # Here you can generate a token or any other method to verify the reset request
    # For simplicity, we'll just render the reset form
    return jsonify({'message': '请重置您的密码', 'user_id': user.id}), 200

@auth.route('/password_reset/<int:user_id>', methods=['POST'])
def password_reset(user_id):
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({'message': '缺少必要的字段'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

    return jsonify({'message': '密码重置成功'}), 200

@auth.route('/password_reset', methods=['GET'])
def show_password_reset_request():
    return render_template('password_reset_request.html')

@auth.route('/password_reset/<int:user_id>', methods=['GET'])
def show_password_reset(user_id):
    return render_template('password_reset.html', user_id=user_id)


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))