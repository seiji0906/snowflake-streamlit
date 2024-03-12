import streamlit as st
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import pd_writer

# Snowflake接続情報
conn_info = {
    'user': 'YOUR_USER',
    'password': 'YOUR_PASSWORD',
    'account': 'YOUR_ACCOUNT',
    'warehouse': 'YOUR_WAREHOUSE',
    'database': 'YOUR_DATABASE',
    'schema': 'YOUR_SCHEMA',
}

# Streamlitアプリのタイトル
st.title('Snowflakeデータ分析アプリ')

# Snowflakeに接続
conn = snowflake.connector.connect(**conn_info)

@st.cache(ttl=600)
def load_data(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
    return df

# ユーザーが実行したいクエリを入力
user_query = st.text_area("SQLクエリを入力してください", 'SELECT * FROM YOUR_TABLE LIMIT 100')

# データを読み込む
if st.button('データを読み込む'):
    df = load_data(user_query)
    st.write(df)

# ここにデータ分析や可視化のコードを追加
