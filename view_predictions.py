import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/predictions.db')
cursor = conn.cursor()

# Query data
cursor.execute("SELECT * FROM predictions;")  # Modify table name as needed
rows = cursor.fetchall()

# Print results
for row in rows:
    print(row)

# Close the connection
conn.close()