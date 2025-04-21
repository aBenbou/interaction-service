# Save as reset_migrations.py
import psycopg2
import os
import sys

def reset_migrations():
    conn_string = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/interaction_service')
    
    try:
        print(f"Connecting to database: {conn_string}")
        conn = psycopg2.connect(conn_string)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Check if alembic_version table exists
        print("Checking for alembic_version table...")
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
        has_alembic = cursor.fetchone()[0]
        
        if has_alembic:
            print("Dropping alembic_version table...")
            cursor.execute("DROP TABLE alembic_version")
            conn.commit()
            print("alembic_version table dropped")
        else:
            print("alembic_version table does not exist")
        
        cursor.close()
        conn.close()
        print("Migration reset complete")
        return True
    except Exception as e:
        print(f"Migration reset failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if reset_migrations():
        sys.exit(0)
    else:
        sys.exit(1)