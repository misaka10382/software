import os

class Config:
    # 设置密钥，用于保护重要数据
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 设置数据库连接，用于存储用户信息
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    # 设置数据库跟踪修改，用于记录用户操作
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    