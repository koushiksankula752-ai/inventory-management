from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify  # type: ignore
from forms import LoginForm, ItemForm
from models import db, InventoryItem, AuditLog
from flask_login import login_required, current_user, LoginManager, UserMixin  # type: ignore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me-for-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Simple authentication (replace with real auth)
        if form.username.data == 'admin' and form.password.data == 'password':
            session['user_id'] = 1
            return redirect(url_for('list_items'))
        flash('Invalid credentials', 'error')
    return render_template('login.html', form=form)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if request.method == 'POST' and form.validate_on_submit():
        item = InventoryItem(
            product_name=form.product_name.data,
            sku=form.sku.data,
            category=form.category.data or '',
            quantity=int(form.quantity.data or 0),
            supplier=form.supplier.data or '',
            price=float(form.price.data or 0.0),
            location=form.location.data or ''
        )
        db.session.add(item)
        db.session.commit()
        # audit
        user_id = session.get('user_id') or getattr(current_user, 'id', None)
        log = AuditLog(user_id=user_id, action='CREATE', item_id=item.id, details=f'Created item {item.product_name}')
        db.session.add(log)
        db.session.commit()
        flash('Item added', 'success')
        return redirect(url_for('list_items'))
    return render_template('add.html', form=form)

@app.route('/items')
@login_required
def list_items():
    items = InventoryItem.query.all()
    return render_template('list.html', items=items)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    if request.method == 'POST' and form.validate_on_submit():
        old = f'quantity={item.quantity}, price={item.price}, location={item.location}'
        # update fields from the form
        item.product_name = form.product_name.data
        item.sku = form.sku.data
        item.category = form.category.data or ''
        item.quantity = int(form.quantity.data or 0)
        item.supplier = form.supplier.data or ''
        item.price = float(form.price.data or 0.0)
        item.location = form.location.data or ''
        db.session.commit()
        # audit
        user_id = session.get('user_id') or getattr(current_user, 'id', None)
        details = f'Updated from {old} to quantity={item.quantity}, price={item.price}, location={item.location}'
        log = AuditLog(user_id=user_id, action='UPDATE', item_id=item.id, details=details)
        db.session.add(log)
        db.session.commit()
        flash('Item updated', 'success')
        return redirect(url_for('list_items'))
    return render_template('edit.html', item=item, form=form)


@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    user_id = session.get('user_id') or getattr(current_user, 'id', None)
    log = AuditLog(user_id=user_id, action='DELETE', item_id=item_id, details=f'Deleted item id {item_id}')
    db.session.add(log)
    db.session.commit()
    flash('Item deleted', 'success')
    return redirect(url_for('list_items'))


# Simple REST API endpoints (JSON)
@app.route('/api/items', methods=['GET', 'POST'])
def api_items():
    if request.method == 'GET':
        items = InventoryItem.query.all()
        return jsonify([{
            'id': i.id, 'product_name': i.product_name, 'sku': i.sku,
            'category': i.category, 'quantity': i.quantity, 'supplier': i.supplier,
            'price': i.price, 'location': i.location
        } for i in items])
    data = request.get_json() or {}
    if not data.get('sku'):
        return jsonify({'error': 'Missing sku'}), 400
    if InventoryItem.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'SKU exists'}), 400
    item = InventoryItem(
        product_name=data.get('product_name', ''), sku=data['sku'],
        category=data.get('category', ''), quantity=data.get('quantity', 0),
        supplier=data.get('supplier', ''), price=data.get('price', 0.0), location=data.get('location', '')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id}), 201


@app.route('/api/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def api_item(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    if request.method == 'GET':
        return jsonify({
            'id': item.id, 'product_name': item.product_name, 'sku': item.sku,
            'category': item.category, 'quantity': item.quantity, 'supplier': item.supplier,
            'price': item.price, 'location': item.location
        })
    if request.method == 'PUT':
        data = request.get_json() or {}
        item.product_name = data.get('product_name', item.product_name)
        item.quantity = data.get('quantity', item.quantity)
        item.sku = data.get('sku', item.sku)
        item.category = data.get('category', item.category)
        item.supplier = data.get('supplier', item.supplier)
        item.price = data.get('price', item.price)
        item.location = data.get('location', item.location)
        db.session.commit()
        return jsonify({'status': 'ok'})
    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'deleted'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
