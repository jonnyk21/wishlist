from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL on Render.com
    db_url = os.environ.get('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Use SQLite locally
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'

INVITE_TOKEN = os.environ.get('INVITE_TOKEN', 'your-secret-token-change-in-production')

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'invite'

db.init_app(app)
login_manager.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    wishes = db.relationship('Wish', backref='owner', lazy=True, foreign_keys='Wish.user_id', cascade='all, delete-orphan')
    reserved_wishes = db.relationship('Wish', backref='reserved_by', lazy=True, foreign_keys='Wish.reserved_by_id')

    def delete_account(self):
        # Remove all reservations made by this user
        Wish.query.filter_by(reserved_by_id=self.id).update({'reserved_by_id': None})
        # Delete the user and their wishes
        db.session.delete(self)
        db.session.commit()

class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(200))
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reserved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def fetch_metadata(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title if name is not provided
            if not self.name:
                title = soup.find('title')
                self.name = title.string if title else urlparse(self.url).netloc
            
            # Find thumbnail
            og_image = soup.find('meta', property='og:image')
            if og_image:
                self.thumbnail_url = og_image.get('content')
            else:
                # Try to find the first image as fallback
                first_img = soup.find('img')
                if first_img and first_img.get('src'):
                    img_src = first_img.get('src')
                    if not img_src.startswith('http'):
                        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.url))
                        img_src = base_url + img_src
                    self.thumbnail_url = img_src
        except:
            if not self.name:
                self.name = urlparse(self.url).netloc

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_invite_token():
    token = request.args.get('token')
    return token == INVITE_TOKEN

@app.before_request
def check_access():
    # Allow access to static files and the invite page
    if request.path.startswith('/static/') or request.endpoint == 'invite':
        return
    
    # Check if user is authenticated or has valid token
    if not current_user.is_authenticated and not check_invite_token():
        return redirect(url_for('invite'))

@app.route('/invite')
def invite():
    if check_invite_token():
        return redirect(url_for('login', token=INVITE_TOKEN))
    return render_template('invite.html')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login', token=request.args.get('token', '')))

@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Please enter your name')
            return redirect(url_for('login'))
            
        # Find or create user
        user = User.query.filter_by(name=name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/add_wish', methods=['POST'])
@login_required
def add_wish():
    url = request.form.get('url')
    name = request.form.get('name')
    
    new_wish = Wish(
        url=url,
        name=name,
        user_id=current_user.id
    )
    
    new_wish.fetch_metadata()
    db.session.add(new_wish)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_wish/<int:wish_id>', methods=['POST'])
@login_required
def delete_wish(wish_id):
    wish = Wish.query.get_or_404(wish_id)
    if wish.user_id == current_user.id:
        db.session.delete(wish)
        db.session.commit()
        flash('Wish deleted successfully')
    else:
        flash('You cannot delete this wish')
    return redirect(url_for('dashboard'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    current_user.delete_account()
    logout_user()
    flash('Your account has been deleted')
    return redirect(url_for('index'))

@app.route('/reserve_wish/<int:wish_id>', methods=['POST'])
@login_required
def reserve_wish(wish_id):
    wish = Wish.query.get_or_404(wish_id)
    if wish.user_id != current_user.id:  # Can't reserve your own wish
        wish.reserved_by_id = current_user.id
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/unreserve_wish/<int:wish_id>', methods=['POST'])
@login_required
def unreserve_wish(wish_id):
    wish = Wish.query.get_or_404(wish_id)
    if wish.reserved_by_id == current_user.id:
        wish.reserved_by_id = None
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
