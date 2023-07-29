import psycopg2
  
conn = psycopg2.connect(database="test",
                        user='airflow', password='airflow', 
                        host='127.0.0.1', port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

sql2 = '''COPY orders(order_id,date,product_name,quantity)
FROM '/data/Orders.csv'
DELIMITER ','
CSV HEADER;'''

cursor.execute(sql2)

sql3 = '''select * from orders;'''
cursor.execute(sql3)
for i in cursor.fetchall():
    print(i)
  
conn.commit()
conn.close()
