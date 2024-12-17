"""Add priority column to wishes

This migration adds a priority column to the wishes table.
"""

from app import db
from sqlalchemy.sql import text
from sqlalchemy import inspect

def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    """Add priority column to wishes table."""
    if not column_exists('wish', 'priority'):
        with db.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE wish 
                ADD COLUMN priority INTEGER DEFAULT 2
            """))
            conn.commit()

def downgrade():
    """Remove priority column from wishes table."""
    if column_exists('wish', 'priority'):
        # SQLite doesn't support DROP COLUMN in older versions
        # We need to recreate the table without the column
        with db.engine.connect() as conn:
            conn.execute(text("""
                BEGIN TRANSACTION;
                
                CREATE TEMPORARY TABLE wish_backup (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(500) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(500),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL
                );
                
                INSERT INTO wish_backup 
                SELECT id, url, name, thumbnail_url, created_at, user_id
                FROM wish;
                
                DROP TABLE wish;
                
                CREATE TABLE wish (
                    id INTEGER PRIMARY KEY,
                    url VARCHAR(500) NOT NULL,
                    name VARCHAR(200),
                    thumbnail_url VARCHAR(500),
                    created_at DATETIME,
                    user_id INTEGER NOT NULL
                );
                
                INSERT INTO wish 
                SELECT id, url, name, thumbnail_url, created_at, user_id
                FROM wish_backup;
                
                DROP TABLE wish_backup;
                
                COMMIT;
            """))
            conn.commit()
