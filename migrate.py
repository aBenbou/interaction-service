# migrate.py
#!/usr/bin/env python3
import os
import sys
import argparse
import datetime
import sqlite3
import psycopg2
import re
from app.config import Config

def get_timestamp():
    """Generate a timestamp for migration files in the format YYYYMMDDHHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def create_migration(name):
    """Create new migration files with the given name"""
    timestamp = get_timestamp()
    filename = f"{timestamp}-{name.replace(' ', '_').lower()}.sql"
    
    # Create up migration file
    up_path = os.path.join("migrations", "up", filename)
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(up_path), exist_ok=True)
    
    with open(up_path, "w") as f:
        f.write(f"-- Migration: {name}\n")
        f.write(f"-- Created at: {datetime.datetime.now().isoformat()}\n\n")
        f.write("-- Write your UP migration SQL here\n\n")
    
    # Create down migration file
    down_path = os.path.join("migrations", "down", filename)
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(down_path), exist_ok=True)
    
    with open(down_path, "w") as f:
        f.write(f"-- Migration: {name}\n")
        f.write(f"-- Created at: {datetime.datetime.now().isoformat()}\n\n")
        f.write("-- Write your DOWN migration SQL here\n\n")
    
    print(f"Created migration files:")
    print(f"  - {up_path}")
    print(f"  - {down_path}")

def ensure_migrations_table(conn, cursor, is_postgres=False):
    """Ensure the migrations tracking table exists"""
    if is_postgres:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
    conn.commit()

def get_applied_migrations(cursor):
    """Get list of applied migrations"""
    cursor.execute("SELECT name FROM migrations ORDER BY id")
    return [row[0] for row in cursor.fetchall()]

def run_migration(conn, cursor, migration_path, migration_name, is_postgres=False):
    """Run a single migration file"""
    with open(migration_path, "r") as f:
        sql = f.read()
    
    # Execute the migration
    cursor.execute(sql)
    
    # Record the migration
    if is_postgres:
        cursor.execute("INSERT INTO migrations (name) VALUES (%s)", (migration_name,))
    else:
        cursor.execute("INSERT INTO migrations (name) VALUES (?)", (migration_name,))
    
    conn.commit()
    print(f"Applied: {migration_name}")

def remove_migration(conn, cursor, migration_path, migration_name, is_postgres=False):
    """Remove a migration"""
    with open(migration_path, "r") as f:
        sql = f.read()
    
    # Execute the migration
    cursor.execute(sql)
    
    # Remove the migration record
    if is_postgres:
        cursor.execute("DELETE FROM migrations WHERE name = %s", (migration_name,))
    else:
        cursor.execute("DELETE FROM migrations WHERE name = ?", (migration_name,))
    
    conn.commit()
    print(f"Reverted: {migration_name}")

def run_migrations(direction, steps=None):
    """Run migrations in the specified direction (up or down)"""
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    
    # Determine database type
    is_postgres = db_uri.startswith('postgresql')
    
    if is_postgres:
        # Parse connection parameters from URI
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_uri)
        if match:
            user, password, host, port, dbname = match.groups()
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        else:
            raise ValueError(f"Could not parse PostgreSQL URI: {db_uri}")
    else:
        # Use SQLite for testing or development
        db_path = db_uri.replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    ensure_migrations_table(conn, cursor, is_postgres)
    
    applied_migrations = get_applied_migrations(cursor)
    
    if direction == 'up':
        # Get all migration files
        migration_dir = os.path.join("migrations", "up")
        if not os.path.exists(migration_dir):
            print(f"Migration directory '{migration_dir}' does not exist.")
            return
            
        migration_files = sorted(os.listdir(migration_dir))
        
        # Filter out already applied migrations
        pending_migrations = [f for f in migration_files if f not in applied_migrations]
        
        # Apply step limit if specified
        if steps is not None:
            pending_migrations = pending_migrations[:steps]
        
        # Apply migrations
        for migration in pending_migrations:
            migration_path = os.path.join("migrations", "up", migration)
            run_migration(conn, cursor, migration_path, migration, is_postgres)
    
    elif direction == 'down':
        # Get applied migrations in reverse order
        migrations_to_revert = list(reversed(applied_migrations))
        
        # Apply step limit if specified
        if steps is not None:
            migrations_to_revert = migrations_to_revert[:steps]
        
        # Revert migrations
        for migration in migrations_to_revert:
            migration_path = os.path.join("migrations", "down", migration)
            if os.path.exists(migration_path):
                remove_migration(conn, cursor, migration_path, migration, is_postgres)
            else:
                print(f"Warning: Down migration file not found for {migration}")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Database migration utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("name", help="Name of the migration")
    
    # Up migration command
    up_parser = subparsers.add_parser("up", help="Run up migrations")
    up_parser.add_argument("--steps", type=int, help="Number of migrations to apply")
    
    # Down migration command
    down_parser = subparsers.add_parser("down", help="Run down migrations")
    down_parser.add_argument("--steps", type=int, help="Number of migrations to revert")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_migration(args.name)
    elif args.command == "up":
        run_migrations("up", args.steps)
    elif args.command == "down":
        run_migrations("down", args.steps)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()