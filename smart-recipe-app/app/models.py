from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # カラーコードをDBで管理
    # リレーション設定：食材データから .category でこのオブジェクトにアクセス可能にする
    ingredients = db.relationship('Ingredient', backref='category_ref', lazy=True)

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    # 第3正規化：カテゴリー名を直接持たず、IDで紐付ける（外部キー）
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    @property
    def category(self):
        return self.category_ref.name
    
    @property
    def category_color(self):
        return self.category_ref.color
