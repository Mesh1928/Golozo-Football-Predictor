import pandas as pd
import pymysql
from sqlalchemy import create_engine


df = pd.read_csv(r'C:\Users\Mac 65-61\Desktop\Disso\CS3607_2211674\CS3607_2211674\future_predictions_withXGBV2.csv')
df = df.where(pd.notnull(df), None)
print(df.dtypes)

conn = pymysql.connect(host='localhost', user='root', password='2468goku')


with conn.cursor() as cursor:
    cursor.execute("CREATE DATABASE IF NOT EXISTS GolozoDB")


conn.close()


engine = create_engine("mysql+pymysql://root:2468goku@localhost/GolozoDB")

conn = pymysql.connect(host='localhost', user='root', password='2468goku', database='GolozoDB')

df.to_sql("matches", con=engine, if_exists="replace", index=False)

