from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Cart

auth = Blueprint('auth', __name__)

@auth.context_processor
def inject_cart_data():
    cart_items = []
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(UserID=current_user.UserID).all()
    return dict(cart_items=cart_items)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(Email=email).first()
        if user and user.Password == password:  # In production, use proper password hashing
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        
        flash('Invalid email or password')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(Email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
            
        new_user = User(
            Email=email,
            Password=password,  # In production, use proper password hashing
            Fullname=name
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main.home'))
        
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))