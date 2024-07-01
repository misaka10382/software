from flask import Flask, jsonify,render_template
from models import db, bcrypt
from routes import auth
from config import Config
from admin_routes import admin
from user_route import users
from flask_session import Session
from doctor_routes import doctors


# 导入Flask类，并创建Flask应用实例
app = Flask(__name__)
# 从Config类中加载配置
app.config.from_object(Config)
# 初始化数据库
db.init_app(app)
# 初始化bcrypt
bcrypt.init_app(app)


app.config['SESSION_TYPE'] = 'filesystem'  # 确保 SESSION_TYPE 设置正确
Session(app)

# 注册auth蓝图，并设置url前缀
app.register_blueprint(auth, url_prefix='/auth')
# 注册users蓝图，并设置url前缀
app.register_blueprint(users,url_prefix='/user')
app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(doctors,url_prefix='/doctor')

# 确保数据库和表已经创建
with app.app_context():
    # 创建所有表
    db.create_all()

# 设置根路由
@app.route('/')
def home():
    # 渲染index.html模板
    return render_template('index.html')

if __name__ == "__main__":
    # 运行Flask应用，debug参数设置为True，表示在调试模式下运行
    app.run(debug=True)
