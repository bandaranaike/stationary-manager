import sqlite3


def remove_empty_stocks(db_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the SQL command to delete stocks with zero stock
        cursor.execute('DELETE FROM stocks WHERE stock = 0')

        # Commit the changes
        conn.commit()
        print("Empty stocks removed successfully.")

    except sqlite3.Error as error:
        print(f"Error while removing empty stocks: {error}")

    finally:
        # Close the database connection
        if conn:
            conn.close()
