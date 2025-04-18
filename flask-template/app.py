import os
from flask import render_template, Flask
from dotenv import load_dotenv
from . import create_app, db
from .models import User, Category, Product, Order, Cart

# Load environment variables
load_dotenv()

# Initialize Flask app
app = create_app()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
