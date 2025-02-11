from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User Model (Farmers & Buyers)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # "farmer" or "buyer"

# Crop Listings
class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Forum Posts
class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        user_type = request.form["user_type"]

        new_user = User(username=username, email=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials, try again.", "danger")

    return render_template("login.html")

# Dashboard (Farmers & Buyers)
@app.route("/dashboard")
@login_required
def dashboard():
    crops = Crop.query.all()
    return render_template("dashboard.html", crops=crops, user_type=current_user.user_type)

# List Crops (Farmers only)
@app.route("/list_crop", methods=["POST"])
@login_required
def list_crop():
    if current_user.user_type == "farmer":
        name = request.form["name"]
        quantity = request.form["quantity"]
        price = request.form["price"]

        new_crop = Crop(name=name, quantity=quantity, price=price, farmer_id=current_user.id)
        db.session.add(new_crop)
        db.session.commit()
        flash("Crop listed successfully!", "success")

    return redirect(url_for("dashboard"))

# Forum Page
@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        new_post = Forum(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash("Forum post added!", "success")

    posts = Forum.query.all()
    return render_template("forum.html", posts=posts)

# Weather API Integration
@app.route("/weather")
def weather():
    api_key = "your_weather_api_key"
    city = "Delhi"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url).json()

    temperature = response["current"]["temp_c"]
    condition = response["current"]["condition"]["text"]
    
    return render_template("weather.html", temperature=temperature, condition=condition)

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database is created inside the app context
    app.run(debug=True)

