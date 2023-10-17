import pandas as pd
import psycopg2

# Чтение данных из .csv файла
data = pd.read_csv('ingredients.csv')

# Подключение к базе данных
conn = psycopg2.connect(
    host='db',
    port='5432',
    user='foodgram_user',
    password='foodgram_password',
    database='foodgram'
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