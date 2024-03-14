import snowflake.connector
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数ファイルの読み込み
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
account = os.getenv('SNOWFLAKE_ACCOUNT')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
database = os.getenv('SNOWFLAKE_DATABASE')
schema = os.getenv('SNOWFLAKE_SCHEMA')

# Snowflakeに接続
def get_data_from_snowflake(query):
    ctx = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    cs = ctx.cursor()
    try:
        cs.execute(query)
        df = cs.fetch_pandas_all()
        return df
    finally:
        cs.close()
        ctx.close()

# Streamlitアプリのタイトル
st.title('Snowflake Data Analysis App')

# ユーザーがクエリを入力
user_query = st.text_input('Enter your query:', 'SELECT * FROM YOUR_TABLE LIMIT 10')

# データの取得と表示
if st.button('Get Data'):
    df = get_data_from_snowflake(user_query)
    st.write(df)