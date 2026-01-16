from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 食材名
    category = db.Column(db.String(50), nullable=False)  # カテゴリー
    quantity = db.Column(db.String(50), nullable=False)  # 分量
    expiry_date = db.Column(db.Date, nullable=False)  # 賞味期限
