import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="diem_xet_tuyen"
)


def query_data(query_string):

    # Kiểm tra kết nối
    if conn.is_connected():
        cursor = conn.cursor()

        cursor.execute(query_string)
        rows = cursor.fetchall()
        conn.close()
        return rows
    else:
        return None
