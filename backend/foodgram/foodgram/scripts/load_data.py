import pandas as pd
import psycopg2

# Чтение данных из .csv файла
def load_data():
    data = pd.read_csv('../../api/scripts/ingredients.csv')

    # Подключение к базе данных
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )
    cursor = conn.cursor()

    # Загрузка данных в базу данных
    for _, row in data.iterrows():
        query = f"INSERT INTO ingredients (column1, column2) VALUES ('{row['column1']}', '{row['column2']}')"
        cursor.execute(query)

    # Сохранение изменений и закрытие соединения
    conn.commit()
    cursor.close()
    conn.close()