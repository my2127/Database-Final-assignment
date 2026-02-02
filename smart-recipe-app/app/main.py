from flask import Flask, render_template, request, redirect, url_for
from models import db, Ingredient, Category, Recipe, RecipeIngredient
from datetime import datetime, date
import os
from sqlalchemy import text  # 1. これをインポートに追加

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 初回起動時にカテゴリーのマスターデータを作成する関数
def setup_master_data():
    if Category.query.first() is None:
        initial_data = [
            ('野菜', '#d4edda'), ('肉', '#f8d7da'), ('魚', '#caf0f8'),
            ('果物', '#ffd8b1'), ('乳製品', '#cce5ff'), ('冷凍食品', '#d0f4de'),
            ('飲み物', '#dec0f1'), ('惣菜', '#faedcd'), ('お菓子', '#fde2e4'),
            ('加工食品', '#fff3cd'), ('調味料', '#ccd5ae'), ('その他', '#e2e3e5')
        ]
        for name, color in initial_data:
            db.session.add(Category(name=name, color=color))
        db.session.commit()
        print("Master data initialized!")

def wait_for_db():
    """データベース接続が確立するまで待機"""
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection established!")
            return True
        except Exception as e:
            print(f"Waiting for database... ({i+1}/{max_retries}) - Error: {e}")
            time.sleep(2)
    return False

with app.app_context():
    if wait_for_db():
        db.create_all()
        setup_master_data()
    else:
        print("Failed to connect to database after multiple retries")
        exit(1)

@app.route('/')
def index():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', '')

    query = Ingredient.query
    if search:
        query = query.filter(Ingredient.name.contains(search))
    if category_id:
        query = query.filter(Ingredient.category_id == category_id)

    ingredients = query.order_by(Ingredient.expiry_date).all()
    all_categories = Category.query.all()

    today = date.today()

    # 統計計算（バックエンドで実行）
    total_items = len(ingredients)
    expired_count = 0
    warning_count = 0

    for ing in ingredients:
        ing.remaining_days = (ing.expiry_date - today).days

        # 期限状況の判定基準:
        # - 0日以下（当日を含む）：期限切れ
        # - 1〜3日：期限間近
        if ing.remaining_days <= 0:
            expired_count += 1
        elif ing.remaining_days <= 3:
            warning_count += 1

    return render_template('index.html',
                           ingredients=ingredients,
                           search=search,
                           selected_category=category_id,
                           categories=all_categories,
                           total_items=total_items,
                           warning_count=warning_count,
                           expired_count=expired_count)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    category_id = request.form['category_id']
    quantity = request.form['quantity']
    expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()

    new_ing = Ingredient(name=name, category_id=category_id, quantity=quantity, expiry_date=expiry_date)
    db.session.add(new_ing)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    ing = Ingredient.query.get_or_404(id)
    all_categories = Category.query.all()

    if request.method == 'POST':
        ing.name = request.form['name']
        ing.category_id = request.form['category_id']
        ing.quantity = request.form['quantity']
        ing.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', ingredient=ing, categories=all_categories)

@app.route('/delete/<int:id>')
def delete(id):
    ing = Ingredient.query.get_or_404(id)
    db.session.delete(ing)
    db.session.commit()
    return redirect(url_for('index'))

# レシピ関連のルート
@app.route('/recipes')
def recipes():
    recipes_list = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('recipes.html', recipes=recipes_list)

@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        instructions = request.form['instructions']

        # 新しいレシピを作成
        new_recipe = Recipe(title=title, instructions=instructions)
        db.session.add(new_recipe)
        db.session.flush()  # IDを取得するため

        # 材料の追加
        category_ids = request.form.getlist('category_ids[]')
        quantities = request.form.getlist('quantities[]')

        for category_id, quantity in zip(category_ids, quantities):
            if category_id and quantity:  # 空の入力はスキップ
                recipe_ingredient = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    category_id=int(category_id),
                    quantity=quantity
                )
                db.session.add(recipe_ingredient)

        db.session.commit()
        return redirect(url_for('recipes'))

    # GETリクエストの場合：カテゴリーリストを取得してフォームを表示
    categories = Category.query.order_by(Category.name).all()
    return render_template('add_recipe.html', categories=categories)

@app.route('/recipes/<int:id>')
def recipe_detail(id):
    recipe = Recipe.query.get_or_404(id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/recipes/delete/<int:id>')
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('recipes'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
