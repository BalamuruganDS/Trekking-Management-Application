import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'trekking_app.db')


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
existing_columns = {
    row[1]
    for row in cursor.fetchall()
}


columns_to_add = {
    'address': 'VARCHAR(250)',
    'age': 'INTEGER',
    'has_disability': 'BOOLEAN NOT NULL DEFAULT 0',
    'disability_description': 'VARCHAR(500)'
}


for column_name, column_type in columns_to_add.items():

    if column_name not in existing_columns:

        cursor.execute(
            f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
        )

        print(f"Added column: {column_name}")

    else:
        print(f"Already exists: {column_name}")


conn.commit()
conn.close()

print("Profile database update completed.")