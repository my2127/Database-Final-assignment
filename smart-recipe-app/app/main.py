from flask import Flask, render_template, request, redirect, url_for
from models import db, Ingredient
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

categories = ['野菜', '肉', '乳製品', '加工食品', 'その他']
category_colors = {'野菜': '#d4edda', '肉': '#f8d7da', '乳製品': '#cce5ff', '加工食品': '#fff3cd', 'その他': '#e2e3e5'}

@app.route('/')
def index():
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    query = Ingredient.query
    if search:
        query = query.filter(Ingredient.name.contains(search))
    if category_filter:
        query = query.filter(Ingredient.category == category_filter)
    ingredients = query.order_by(Ingredient.expiry_date).all()
    today = date.today()
    for ing in ingredients:
        ing.remaining_days = (ing.expiry_date - today).days
    return render_template('index.html', ingredients=ingredients, search=search, category=category_filter, categories=categories, category_colors=category_colors)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    category = request.form['category']
    quantity = request.form['quantity']
    expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
    new_ing = Ingredient(name=name, category=category, quantity=quantity, expiry_date=expiry_date)
    db.session.add(new_ing)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    ing = Ingredient.query.get_or_404(id)
    db.session.delete(ing)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
