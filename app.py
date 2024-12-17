from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from Levenshtein import distance
from enum import Enum
import logging
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError, OperationalError
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Connection management settings
MAX_RETRIES = 3
RETRY_DELAY = 0.1  # seconds
HEALTH_CHECK_INTERVAL = 30  # seconds
last_health_check = 0
connection_errors = 0
MAX_CONNECTION_ERRORS = 3

@contextmanager
def safe_db_session():
    """Context manager for safe database operations."""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        raise

def check_db_connection():
    """Check database connection and attempt to reconnect if needed."""
    global last_health_check, connection_errors
    
    current_time = datetime.utcnow().timestamp()
    if current_time - last_health_check < HEALTH_CHECK_INTERVAL:
        return connection_errors < MAX_CONNECTION_ERRORS
        
    try:
        with safe_db_session() as session:
            session.execute(text('SELECT 1'))
            last_health_check = current_time
            connection_errors = 0  # Reset error count on successful connection
            return True
    except (DBAPIError, SQLAlchemyError) as e:
        logger.error(f"Database connection check failed: {str(e)}")
        connection_errors += 1
        
        if connection_errors >= MAX_CONNECTION_ERRORS:
            logger.error("Maximum connection errors reached")
            return False
            
        try:
            db.session.remove()
            db.engine.dispose()
            with safe_db_session() as session:
                session.execute(text('SELECT 1'))
            last_health_check = current_time
            connection_errors = 0  # Reset error count on successful reconnection
            return True
        except Exception as e:
            logger.error(f"Database reconnection failed: {str(e)}")
            return False

def retry_db_operation(operation):
    """Retry database operations with exponential backoff."""
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            if not check_db_connection():
                raise OperationalError("Database connection failed", None, None)
                
            with safe_db_session() as session:
                return operation()
                
        except OperationalError as e:
            last_error = e
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Max retries reached for database operation: {str(e)}")
                raise
            delay = RETRY_DELAY * (2 ** attempt)
            logger.warning(f"Database operation failed, retrying in {delay}s. Error: {str(e)}")
            time.sleep(delay)
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise

class Priority(Enum):
    MUST_HAVE = 1
    WOULD_BE_NICE = 2
    MAYBE = 3

    @staticmethod
    def get_label(value):
        labels = {
            1: "Muss ich haben ",
            2: "Wäre schön ",
            3: "Vielleicht "
        }
        return labels.get(value, "Keine Priorität")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    wishes = db.relationship('Wish', backref='owner', lazy=True, cascade='all, delete-orphan')

    def delete_account(self):
        def _delete():
            db.session.delete(self)
            db.session.commit()
        return retry_db_operation(_delete)

class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(200))
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.Integer, default=2)  # Default to WOULD_BE_NICE

    @property
    def priority_label(self):
        return Priority.get_label(self.priority)

    def fetch_metadata(self):
        """Fetch metadata from URL and set name and thumbnail."""
        if not self.url:
            return

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=5)
            response.raise_for_status()  # Raise exception for bad status codes
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title if name is not provided
            if not self.name:
                # Try meta title first
                meta_title = soup.find('meta', property='og:title')
                if meta_title and meta_title.get('content'):
                    self.name = meta_title.get('content')
                else:
                    # Fall back to regular title
                    title = soup.find('title')
                    self.name = title.string.strip() if title and title.string else None
                
                # If still no name, use the domain name
                if not self.name:
                    self.name = urlparse(self.url).netloc
                
                # Limit name length
                self.name = self.name[:200] if self.name else None
            
            # Find thumbnail
            # Try og:image first
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                self.thumbnail_url = og_image.get('content')
            else:
                # Try other meta image tags
                meta_image = (
                    soup.find('meta', property='twitter:image') or
                    soup.find('meta', {'name': 'thumbnail'}) or
                    soup.find('link', rel='image_src')
                )
                if meta_image:
                    self.thumbnail_url = meta_image.get('content') or meta_image.get('href')
                else:
                    # Fall back to first image
                    first_img = soup.find('img', src=True)
                    if first_img:
                        img_src = first_img.get('src')
                        if img_src:
                            # Handle relative URLs
                            if not img_src.startswith(('http://', 'https://')):
                                base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.url))
                                img_src = urljoin(base_url, img_src)
                            self.thumbnail_url = img_src

        except Exception as e:
            logger.error(f"Error fetching metadata for {self.url}: {str(e)}")
            # Ensure we at least have a name
            if not self.name:
                self.name = urlparse(self.url).netloc

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

    # Database configuration
    if os.environ.get('DATABASE_URL'):
        db_url = os.environ.get('DATABASE_URL')
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        # Add connection pooling settings
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'pool_recycle': 1800,  # Recycle connections after 30 minutes
            'pool_pre_ping': True,  # Enable connection health checks
            'pool_timeout': 30,     # Connection timeout in seconds
            'max_overflow': 10,     # Allow up to 10 connections over pool_size
            'echo': True,           # Log all SQL statements in development
            'echo_pool': True       # Log connection pool events
        }
    else:
        # Use SQLite locally
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'
        # SQLite-specific settings
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'echo': True
        }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'invite'

    # Create tables within app context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def check_invite_token():
        # Skip token check in development
        if not os.environ.get('DATABASE_URL'):  # We're in local development
            return True
        token = request.args.get('token')
        return token == os.environ.get('INVITE_TOKEN', 'your-secret-token-change-in-production')

    def find_similar_users(name, threshold=2):
        """Find users with similar names using Levenshtein distance."""
        similar_users = []
        all_users = User.query.all()
        for user in all_users:
            if distance(name.lower(), user.name.lower()) <= threshold:
                similar_users.append(user)
        return similar_users

    @app.before_request
    def check_access():
        # Skip check for static files and error pages
        if request.path.startswith('/static/') or request.endpoint in ['error', 'static']:
            return

        # Skip token check for invite page
        if request.endpoint == 'invite':
            return

        try:
            if not check_db_connection():
                logger.error("Database connection check failed")
                return render_template('error.html'), 503
            
            # If user is authenticated, they can access any page
            if current_user.is_authenticated:
                return
                
            # For login page, only check token if it's a GET request
            if request.endpoint == 'login' and request.method == 'POST':
                return
                
            # Check invite token for all other pages
            if not check_invite_token():
                return redirect(url_for('invite'))
                
        except Exception as e:
            logger.error(f"Error in check_access: {str(e)}")
            return render_template('error.html'), 503

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        db.session.rollback()
        return render_template('error.html'), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        logger.error(f"Service unavailable: {str(error)}")
        return render_template('error.html'), 503

    @app.route('/')
    def index():
        # If user is logged in, go to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        # If user has token, go to login
        token = request.args.get('token')
        if token and token == os.environ.get('INVITE_TOKEN'):
            return redirect(url_for('login', token=token))
        # Otherwise go to invite page
        return redirect(url_for('invite'))

    @app.route('/invite')
    def invite():
        # If user already has valid token, go to login
        token = request.args.get('token')
        if token and token == os.environ.get('INVITE_TOKEN'):
            return redirect(url_for('login', token=token))
        # Otherwise show invite page
        return render_template('invite.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If user is already logged in, go to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        # On GET request, verify token
        if request.method == 'GET':
            token = request.args.get('token')
            if not token or token != os.environ.get('INVITE_TOKEN'):
                return redirect(url_for('invite'))

        if request.method == 'POST':
            name = request.form.get('name')
            existing_user_id = request.form.get('existing_user')
            
            if not name and not existing_user_id:
                flash('Please enter your name')
                return redirect(url_for('login'))
            
            if existing_user_id:
                # User chose to log in as existing user
                user = User.query.get(existing_user_id)
                if user:
                    login_user(user)
                    return redirect(url_for('dashboard'))
                
            # Check for similar usernames
            similar_users = find_similar_users(name)
            if similar_users and 'confirm_new_user' not in request.form:
                # Show confirmation page with similar users
                return render_template('login.html', similar_users=similar_users, attempted_name=name)
            
            # If user confirmed new account or no similar users found
            if 'confirm_new_user' in request.form or not similar_users:
                user = User(name=name)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('dashboard'))
                
        return render_template('login.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        users = User.query.all()
        # Sort wishes by priority for each user
        for user in users:
            user.wishes.sort(key=lambda w: (w.priority, -w.id))  # Sort by priority, then newest first
        return render_template('dashboard.html', 
                             users=users,
                             priorities=[(p.value, p.name, Priority.get_label(p.value)) for p in Priority])

    @app.route('/add_wish', methods=['POST'])
    @login_required
    def add_wish():
        url = request.form.get('url', '').strip()
        name = request.form.get('name', '').strip()
        # Always default to priority 2 (two stars)
        priority = 2
        
        if not url:
            flash('Please provide a URL')
            return redirect(url_for('dashboard'))
            
        try:
            # Create wish with basic info
            new_wish = Wish(
                url=url,
                name=name if name else None,  # Only set name if provided
                user_id=current_user.id,
                priority=priority
            )
            
            # Fetch metadata before saving
            new_wish.fetch_metadata()
            
            def _add_wish():
                db.session.add(new_wish)
                db.session.commit()
                
            retry_db_operation(_add_wish)
            flash('Wish added successfully!')
        except Exception as e:
            logger.error(f"Error adding wish: {str(e)}")
            flash('Error adding wish. Please try again.')
            
        return redirect(url_for('dashboard'))

    @app.route('/update_priority/<int:wish_id>', methods=['POST'])
    @login_required
    def update_priority(wish_id):
        wish = Wish.query.get_or_404(wish_id)
        if wish.user_id != current_user.id:
            flash('You can only update your own wishes')
            return redirect(url_for('dashboard'))

        try:
            new_priority = request.form.get('priority')
            if new_priority and new_priority.isdigit():
                wish.priority = int(new_priority)
                db.session.commit()
                flash('Priority updated successfully!')
        except Exception as e:
            flash('Error updating priority. Please try again.')
            logger.error(f"Error updating priority: {str(e)}")

        return redirect(url_for('dashboard'))

    @app.route('/delete_wish/<int:wish_id>', methods=['POST'])
    @login_required
    def delete_wish(wish_id):
        wish = Wish.query.get_or_404(wish_id)
        if wish.user_id == current_user.id:
            def _delete_wish():
                db.session.delete(wish)
                db.session.commit()
            
            try:
                retry_db_operation(_delete_wish)
                flash('Wish deleted successfully')
            except Exception as e:
                flash('Error deleting wish. Please try again.')
                logger.error(f"Error deleting wish: {str(e)}")
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

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        # Redirect to login page with token
        token = os.environ.get('INVITE_TOKEN', '')
        return redirect(url_for('login', token=token))

    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
