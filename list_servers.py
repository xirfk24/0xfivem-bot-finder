import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    cursor.execute('SELECT id, server_name, server_address, initial FROM cfxs')
    rows = cursor.fetchall()

    print('\n' + '='*100)
    print(f'{"ID":<5} | {"Server Name":<30} | {"Address":<30} | {"Initial":<10}')
    print('='*100)

    for row in rows:
        print(f'{row[0]:<5} | {row[1]:<30} | {row[2]:<30} | {row[3]:<10}')

    print('='*100)
    print(f'\nTotal servers: {len(rows)}')

except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
