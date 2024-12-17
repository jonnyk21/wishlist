"""Add priority column to wishes

This migration adds a priority column to the wishes table.
"""

from sqlalchemy import create_engine, inspect, text
import os

def get_engine():
    """Get SQLAlchemy engine."""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return create_engine(db_url or 'sqlite:///wishlist.db')

def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    engine = get_engine()
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    """Add priority column to wishes table."""
    engine = get_engine()
    if not column_exists('wish', 'priority'):
        with engine.begin() as conn:
            conn.execute(text("""
                ALTER TABLE wish 
                ADD COLUMN priority INTEGER DEFAULT 2
            """))

def downgrade():
    """Remove priority column from wishes table."""
    engine = get_engine()
    if column_exists('wish', 'priority'):
        # SQLite doesn't support DROP COLUMN in older versions
        # We need to recreate the table without the column
        with engine.begin() as conn:
            conn.execute(text("""
                BEGIN TRANSACTION;
                
                CREATE TEMPORARY TABLE wish_backup (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(2000) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(2000),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL
                );
                
                INSERT INTO wish_backup 
                SELECT id, url, name, thumbnail_url, created_at, user_id
                FROM wish;
                
                DROP TABLE wish;
                
                CREATE TABLE wish (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(2000) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(2000),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL
                );
                
                INSERT INTO wish 
                SELECT id, url, name, thumbnail_url, created_at, user_id
                FROM wish_backup;
                
                DROP TABLE wish_backup;
                
                COMMIT;
            """))

if __name__ == '__main__':
    upgrade()
