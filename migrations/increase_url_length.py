"""Increase URL field lengths

This migration increases the length of url and thumbnail_url fields in the wish table
to accommodate longer URLs.
"""

from sqlalchemy import create_engine, MetaData, Table, Column, String, text
import os
from datetime import datetime

def upgrade():
    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Create engine
    engine = create_engine(db_url or 'sqlite:///wishlist.db')
    
    # Reflect existing tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Get wish table
    wish = Table('wish', metadata)
    
    # Alter column types
    with engine.begin() as conn:
        if db_url:  # PostgreSQL
            conn.execute(text('''
                ALTER TABLE wish 
                ALTER COLUMN url TYPE VARCHAR(2000),
                ALTER COLUMN thumbnail_url TYPE VARCHAR(2000)
            '''))
        else:  # SQLite
            # Drop wish_new table if it exists from a previous failed migration
            conn.execute(text('DROP TABLE IF EXISTS wish_new'))
            
            # SQLite doesn't support ALTER COLUMN, so we need to:
            # 1. Create new table with desired schema
            # 2. Copy data
            # 3. Drop old table
            # 4. Rename new table
            conn.execute(text('''
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
                INSERT INTO wish_new (id, url, name, thumbnail_url, created_at, user_id, priority)
                SELECT id, url, name, thumbnail_url, created_at, user_id, 2
                FROM wish
            '''))
            conn.execute(text('DROP TABLE wish'))
            conn.execute(text('ALTER TABLE wish_new RENAME TO wish'))

def downgrade():
    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Create engine
    engine = create_engine(db_url or 'sqlite:///wishlist.db')
    
    # Reflect existing tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Get wish table
    wish = Table('wish', metadata)
    
    # Alter column types back
    with engine.begin() as conn:
        if db_url:  # PostgreSQL
            conn.execute(text('''
                ALTER TABLE wish 
                ALTER COLUMN url TYPE VARCHAR(500),
                ALTER COLUMN thumbnail_url TYPE VARCHAR(500)
            '''))
        else:  # SQLite
            # Drop wish_new table if it exists from a previous failed migration
            conn.execute(text('DROP TABLE IF EXISTS wish_new'))
            
            conn.execute(text('''
                CREATE TABLE wish_new (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(500) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(500),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL,
                    priority INTEGER DEFAULT 2,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            '''))
            conn.execute(text('''
                INSERT INTO wish_new (id, url, name, thumbnail_url, created_at, user_id, priority)
                SELECT id, url, name, thumbnail_url, created_at, user_id, 2
                FROM wish
            '''))
            conn.execute(text('DROP TABLE wish'))
            conn.execute(text('ALTER TABLE wish_new RENAME TO wish'))

if __name__ == '__main__':
    upgrade()
