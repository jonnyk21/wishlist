"""Make URL field optional

This migration makes the URL field optional in the wish table.
"""

from sqlalchemy import create_engine, inspect, text
import os

def get_engine():
    """Get SQLAlchemy engine."""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return create_engine(db_url or 'sqlite:///wishlist.db')

def upgrade():
    """Make URL field optional."""
    engine = get_engine()
    
    with engine.begin() as conn:
        if 'postgres' in str(engine.url):  # PostgreSQL
            conn.execute(text('''
                ALTER TABLE wish 
                ALTER COLUMN url DROP NOT NULL
            '''))
        else:  # SQLite
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            conn.execute(text('''
                CREATE TABLE wish_new (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(2000),
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(2000),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL,
                    priority INTEGER DEFAULT 2,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            '''))
            conn.execute(text('''
                INSERT INTO wish_new 
                SELECT id, url, name, thumbnail_url, created_at, user_id, priority
                FROM wish
            '''))
            conn.execute(text('DROP TABLE wish'))
            conn.execute(text('ALTER TABLE wish_new RENAME TO wish'))

def downgrade():
    """Make URL field required again."""
    engine = get_engine()
    
    with engine.begin() as conn:
        if 'postgres' in str(engine.url):  # PostgreSQL
            conn.execute(text('''
                UPDATE wish SET url = '' WHERE url IS NULL;
                ALTER TABLE wish 
                ALTER COLUMN url SET NOT NULL
            '''))
        else:  # SQLite
            conn.execute(text('''
                UPDATE wish SET url = '' WHERE url IS NULL;
                
                CREATE TABLE wish_new (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(2000) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(2000),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL,
                    priority INTEGER DEFAULT 2,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            '''))
            conn.execute(text('''
                INSERT INTO wish_new 
                SELECT id, url, name, thumbnail_url, created_at, user_id, priority
                FROM wish
            '''))
            conn.execute(text('DROP TABLE wish'))
            conn.execute(text('ALTER TABLE wish_new RENAME TO wish'))

if __name__ == '__main__':
    upgrade()
