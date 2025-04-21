# Save as diagnose_db.py
import psycopg2
import os
import sys

def diagnose_database():
    conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
    
    try:
        print(f"Connecting to database: {conn_string}")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Check if we can execute a simple query
        print("Testing basic query...")
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Query result: {result}")
        
        # Check if alembic_version table exists
        print("Checking for alembic_version table...")
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
        has_alembic = cursor.fetchone()[0]
        print(f"alembic_version table exists: {has_alembic}")
        
        if has_alembic:
            # Check current version
            cursor.execute("SELECT version_num FROM alembic_version")
            version = cursor.fetchone()
            print(f"Current alembic version: {version}")
        
        # Check for existing tables
        print("Checking existing tables...")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        print("Database diagnosis complete")
        return True
    except Exception as e:
        print(f"Database diagnosis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if diagnose_database():
        sys.exit(0)
    else:
        sys.exit(1)