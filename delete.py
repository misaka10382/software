from models import db
from app import app

# 删除所有表中的数据
with app.app_context():
    db.drop_all()
