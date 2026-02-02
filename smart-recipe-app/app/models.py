from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # カラーコードをDBで管理
    # リレーション設定：食材データから .category でこのオブジェクトにアクセス可能にする
    ingredients = db.relationship('Ingredient', backref='category_ref', lazy=True)
    # レシピ材料とのリレーション
    recipe_ingredients = db.relationship('RecipeIngredient', backref='category_ref', lazy=True)

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

# レシピモデル（新規追加）
class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # 料理名
    instructions = db.Column(db.Text, nullable=False)  # 作り方
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 多対多リレーション：レシピ材料（中間テーブル経由）
    recipe_ingredients = db.relationship('RecipeIngredient', backref='recipe_ref', lazy=True, cascade='all, delete-orphan')

    @property
    def ingredients_list(self):
        """レシピに必要な材料のリストを返す"""
        return [ri.category_ref.name for ri in self.recipe_ingredients]

# レシピ材料の中間テーブル（多対多リレーション）
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)  # 必要な分量（例: "200g", "1個"）

    # ユニーク制約：同じレシピで同じカテゴリーが重複しないように
    __table_args__ = (db.UniqueConstraint('recipe_id', 'category_id', name='unique_recipe_category'),)

    @property
    def category_name(self):
        return self.category_ref.name

    @property
    def category_color(self):
        return self.category_ref.color
