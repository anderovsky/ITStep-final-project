from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    shelf = db.Column(db.String(50), nullable=False)
    is_lent = db.Column(db.Boolean, default=False)
    lent_to = db.Column(db.String(100), nullable=True)
    lent_date = db.Column(db.DateTime, nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@login_required
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"DEBUG: Login attempt - Username: '{username}'")

        if not username or not password:
            flash('Please fill in both username and password')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        print(f"DEBUG: User found: {user is not None}")

        if user and user.check_password(password):
            login_user(user)
            print("DEBUG: Login successful")
            return redirect(url_for('index'))
        else:
            print("DEBUG: Login failed")
            flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        room = request.form.get('room')
        shelf = request.form.get('shelf')

        if not all([title, author, room, shelf]):
            flash('Please fill in all fields')
            return render_template('add_book.html')

        book = Book(
            title=title,
            author=author,
            room=room,
            shelf=shelf
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('index'))

    return render_template('add_book.html')


# Debug route to check database
@app.route('/debug')
def debug():
    try:
        users = User.query.all()
        books = Book.query.all()
        return f"Users: {len(users)}, Books: {len(books)}"
    except Exception as e:
        return f"Database error: {e}"


def init_db():
    """Initialize database and create default user"""
    print("Creating database tables...")
    db.create_all()
    print("Database tables created!")

    # Check if default user exists
    if not User.query.first():
        print("Creating default user...")
        user = User(username='admin')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print("Default user created: admin/password")
    else:
        print("Default user already exists")


if __name__ == '__main__':
    # IMPORTANT: Create tables within app context
    with app.app_context():
        init_db()

    print("\n" + "=" * 50)
    print("🚀 Flask Library App Starting...")
    print("📍 URL: http://localhost:5000")
    print("🔑 Login: admin / password")
    print("=" * 50 + "\n")

    app.run(debug=True)