import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print('\n' + '='*50)
    print('Tables in database:')
    print('='*50)

    for table in tables:
        print(f'- {table[0]}')

        # Show columns for each table
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f'  Columns: {", ".join([col[1] for col in columns])}')
        print()

    print('='*50)

except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
