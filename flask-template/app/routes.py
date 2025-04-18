from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Product, Cart, Order, OrderItem
from . import db
from sqlalchemy import text

main = Blueprint('main', __name__)

@main.context_processor
def inject_cart_data():
    cart_items = []
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(UserID=current_user.UserID).all()
    return dict(cart_items=cart_items)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/test-db')
def test_db():
    try:
        # Execute a simple query using proper SQLAlchemy text() wrapper
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return jsonify({
            'status': True,
            'message': 'Database connection successful!'
        })
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Database connection failed: {str(e)}'
        })

@main.route('/products')
def get_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@main.route('/products/<int:id>')
def get_product(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

@main.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.ProductID,
        'name': p.Name,
        'description': p.Description,
        'price': float(p.Price),
        'image': p.ImageURL,
        'stock': p.Stock
    } for p in products])

@main.route('/cart')
@login_required
def view_cart():
    # Join Cart and Product tables to get all product details
    cart_items = (
        db.session.query(Cart, Product)
        .join(Product, Cart.ProductID == Product.ProductID)
        .filter(Cart.UserID == current_user.UserID)
        .all()
    )
    
    # Calculate total using product prices
    total = sum(float(item.Product.Price) * item.Cart.Quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@main.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_cart():
    if request.method == 'GET':
        cart_items = Cart.query.filter_by(UserID=current_user.UserID).all()
        return jsonify([{
            'id': item.CartID,
            'product': {
                'id': item.Product.ProductID,
                'name': item.Product.Name,
                'price': float(item.Product.Price),
                'image': item.Product.ImageURL
            },
            'quantity': item.Quantity
        } for item in cart_items])

    elif request.method == 'POST':
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        existing_item = Cart.query.filter_by(
            UserID=current_user.UserID,
            ProductID=product_id
        ).first()

        if existing_item:
            existing_item.Quantity += quantity
        else:
            cart_item = Cart(
                UserID=current_user.UserID,
                ProductID=product_id,
                Quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        return jsonify({'message': 'Added to cart'})

    elif request.method == 'DELETE':
        product_id = request.args.get('product_id')
        Cart.query.filter_by(
            UserID=current_user.UserID,
            ProductID=product_id
        ).delete()
        db.session.commit()
        return jsonify({'message': 'Removed from cart'})

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Get cart items
        cart_items = (
            db.session.query(Cart, Product)
            .join(Product, Cart.ProductID == Product.ProductID)
            .filter(Cart.UserID == current_user.UserID)
            .all()
        )
        
        if not cart_items:
            flash('Your cart is empty')
            return redirect(url_for('main.view_cart'))

        # Calculate total
        total = sum(float(item.Product.Price) * item.Cart.Quantity for item in cart_items)
        
        # Create order
        order = Order(
            UserID=current_user.UserID,
            TotalAmount=total,
            ShippingAddress=request.form.get('shipping_address'),
            Status='Pending'
        )
        db.session.add(order)
        db.session.flush()  # Get OrderID before committing
        
        # Create order items
        for cart, product in cart_items:
            order_item = OrderItem(
                OrderID=order.OrderID,
                ProductID=product.ProductID,
                Quantity=cart.Quantity,
                Price=product.Price
            )
            db.session.add(order_item)
        
        # Clear cart
        Cart.query.filter_by(UserID=current_user.UserID).delete()
        
        db.session.commit()
        flash('Order placed successfully!')
        return redirect(url_for('main.order_confirmation', order_id=order.OrderID))
    
    # GET request - show checkout form
    cart_items = (
        db.session.query(Cart, Product)
        .join(Product, Cart.ProductID == Product.ProductID)
        .filter(Cart.UserID == current_user.UserID)
        .all()
    )
    total = sum(float(item.Product.Price) * item.Cart.Quantity for item in cart_items)
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@main.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.UserID != current_user.UserID:
        abort(403)
    
    order_items = (
        db.session.query(OrderItem, Product)
        .join(Product, OrderItem.ProductID == Product.ProductID)
        .filter(OrderItem.OrderID == order_id)
        .all()
    )
    
    return render_template('order_confirmation.html', order=order, items=order_items)