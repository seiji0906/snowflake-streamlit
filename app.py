import snowflake.connector
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import openai

load_dotenv()

# 環境変数ファイルの読み込み
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
account = os.getenv('SNOWFLAKE_ACCOUNT')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
database = os.getenv('SNOWFLAKE_DATABASE')
schema = os.getenv('SNOWFLAKE_SCHEMA')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Streamlitアプリのタイトル
st.title('Snowflake Data Analysis App')

st.text("""
【アプリ概要】
Snowflake上のデータ（ORDERSテーブル）を取得し、ユーザーが選択したカラムを多様なグラフで表示する
""")

# Markdownを使用してリンクを表示
st.markdown('[今回のLTのきっかけ記事（NTTドコモがStreamlitを社内導入）](https://news.yahoo.co.jp/articles/624de9b79dd9e53164ece15231d6e524a36d8ad4)')

st.markdown('[ソースコード](https://github.com/seiji0906/snowflake-streamlit)')
st.markdown('[サンプルデータ元](https://www.kaggle.com/datasets/kyanyoga/sample-sales-data?resource=download)')

st.markdown('[Streamlit公式ページ](https://streamlit.io)')
st.markdown('[Streamlit Cheat Sheet](https://cheat-sheet.streamlit.app)')

# 目次
st.markdown("""
# 目次
1. [散布図](#section1)
2. [ヒストグラム](#section2)
3. [箱ひげ図](#section3)
4. [棒グラフ](#section4)
5. [円グラフ](#section5)
6. [ヒートマップ](#section6)
7. [Streamlitアプリのユーザー制御について](#section7)
8. [ChatGPT](#section8)
9. [妄想](#section9)
10. [AutoGen](#section10)
""", unsafe_allow_html=True)


###### 文字列表示系
# st.text('Fixed width text')
# st.markdown('_Markdown_') # see #*
# st.caption('Balloons. Hundreds of them...')
# st.latex(r''' e^{i\pi} + 1 = 0 ''')
# st.write('Most objects') # df, err, func, keras!
# st.write(['st', 'is <', 3]) # see *
# st.title('My title')
# st.header('My header')
# st.subheader('My sub')
# st.code('for i in range(8): foo()')

###################snowflakeへ接続########################
# Snowflakeへの接続情報
conn_info = {
    'user': user,
    'password': password,
    'account': account,
    'warehouse': warehouse,
    'database': database,
    'schema': schema
}

# Snowflakeに接続
conn = snowflake.connector.connect(**conn_info)

    # SQLクエリの実行とDataFrameへの読み込み
sql_query = "SELECT * FROM orders"
df = pd.read_sql(sql_query, conn)

# 接続を閉じる
conn.close()
#########################################################


#####################ORDERSテーブルのカラム名とその日本語のマッピング#######################
# 英語のカラム名とそれに対応する日本語訳をマッピングしたオブジェクト
column_mapping = {
    "ORDERNUMBER": "注文番号",
    "QUANTITYORDERED": "注文数量",
    "PRICEEACH": "単価",
    "ORDERLINENUMBER": "注文行番号",
    "SALES": "売上",
    "ORDERDATE": "注文日（データ空です。）",
    "STATUS": "ステータス",
    "QTR_ID": "四半期ID",
    "MONTH_ID": "月ID",
    "YEAR_ID": "年ID",
    "PRODUCTLINE": "製品ライン",
    "MSRP": "希望小売価格",
    "PRODUCTCODE": "製品コード",
    "CUSTOMERNAME": "顧客名",
    "PHONE": "電話番号",
    "ADDRESSLINE1": "住所1",
    "ADDRESSLINE2": "住所2",
    "CITY": "市区町村",
    "STATE": "都道府県",
    "POSTALCODE": "郵便番号",
    "COUNTRY": "国",
    "TERRITORY": "地域",
    "CONTACTLASTNAME": "担当者姓",
    "CONTACTFIRSTNAME": "担当者名",
    "DEALSIZE": "取引規模"
}
############################################################################################



############################### 散布図 #####################################
st.markdown('<a name="section1"></a>', unsafe_allow_html=True)
st.header('散布図')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# 日本語のカラム名のリストを選択肢として渡す
japanese_column_names = list(column_mapping.values())
selected_x_japanese = st.selectbox('X軸に使用するカラムを選択してください', japanese_column_names, index=0, key='scatter_x')
selected_y_japanese = st.selectbox('Y軸に使用するカラムを選択してください', japanese_column_names, index=1, key='scatter_y')

# 選択された日本語名から英語のカラム名を逆引き
selected_x_english = list(column_mapping.keys())[japanese_column_names.index(selected_x_japanese)]
selected_y_english = list(column_mapping.keys())[japanese_column_names.index(selected_y_japanese)]


# 散布図を表示
fig = px.scatter(df, x=selected_x_english, y=selected_y_english, title=f'{column_mapping[selected_x_english]} vs {column_mapping[selected_y_english]}')
st.plotly_chart(fig)
############################################################################


#############################ヒストグラム##################################
st.markdown('<a name="section2"></a>', unsafe_allow_html=True)
# ヒストグラムセクション
st.header('ヒストグラム')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# ヒストグラムのカラム選択。キーを使って散布図のセレクトボックスと区別します。
selected_histogram_japanese = st.selectbox('ヒストグラムに使用するカラムを選択してください', japanese_column_names, index=0, key='histogram_select')
selected_histogram_english = list(column_mapping.keys())[japanese_column_names.index(selected_histogram_japanese)]

# 選択されたカラムに基づいてヒストグラムを描画
fig = px.histogram(df, x=selected_histogram_english, title=f'{column_mapping[selected_histogram_english]}のヒストグラム')
st.plotly_chart(fig)
############################################################################

##################################箱ひげ図##################################
st.markdown('<a name="section3"></a>', unsafe_allow_html=True)
# 箱ひげ図セクション
st.header('箱ひげ図')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# 箱ひげ図のカラム選択。キーを使って他のセレクトボックスと区別します。
selected_boxplot_japanese = st.selectbox('箱ひげ図に使用するカラムを選択してください', japanese_column_names, index=0, key='boxplot_select')
selected_boxplot_english = list(column_mapping.keys())[japanese_column_names.index(selected_boxplot_japanese)]

# 選択されたカラムに基づいて箱ひげ図を描画
fig = px.box(df, y=selected_boxplot_english, title=f'{column_mapping[selected_boxplot_english]}の箱ひげ図')
st.plotly_chart(fig)
#############################################################################

####################################棒グラフ#################################
st.markdown('<a name="section4"></a>', unsafe_allow_html=True)
# 棒グラフセクション
st.header('棒グラフ')
# 棒グラフのカテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_bar_category_japanese = st.selectbox('棒グラフのカテゴリとして使用するカラムを選択してください', japanese_column_names, index=0, key='bar_category_select')
# 棒グラフの値カラム選択
selected_bar_value_japanese = st.selectbox('棒グラフの値として使用するカラムを選択してください', japanese_column_names, index=1, key='bar_value_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_bar_category_english = list(column_mapping.keys())[japanese_column_names.index(selected_bar_category_japanese)]
selected_bar_value_english = list(column_mapping.keys())[japanese_column_names.index(selected_bar_value_japanese)]

# 選択されたカラムに基づいて棒グラフを描画
fig = px.bar(df, x=selected_bar_category_english, y=selected_bar_value_english, title=f'{column_mapping[selected_bar_category_english]}による{column_mapping[selected_bar_value_english]}の棒グラフ')
st.plotly_chart(fig)
#############################################################################

#####################################円グラフ#################################
st.markdown('<a name="section5"></a>', unsafe_allow_html=True)
# 円グラフセクション
st.header('円グラフ')
# 円グラフのカテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_pie_chart_japanese = st.selectbox('円グラフに使用するカテゴリカラムを選択してください', japanese_column_names, index=0, key='pie_chart_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_pie_chart_english = list(column_mapping.keys())[japanese_column_names.index(selected_pie_chart_japanese)]

# 選択されたカラムに基づいて円グラフを描画
fig = px.pie(df, names=selected_pie_chart_english, title=f'{column_mapping[selected_pie_chart_english]}の円グラフ')
st.plotly_chart(fig)
###############################################################################


###################################ヒートマップ#################################
st.markdown('<a name="section6"></a>', unsafe_allow_html=True)
# ヒートマップセクション
st.header('ヒートマップ')
# ヒートマップのX軸カテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_heatmap_x_japanese = st.selectbox('ヒートマップのX軸に使用するカテゴリカラムを選択してください', japanese_column_names, index=0, key='heatmap_x_select')
# ヒートマップのY軸カテゴリカラム選択。
selected_heatmap_y_japanese = st.selectbox('ヒートマップのY軸に使用するカテゴリカラムを選択してください', japanese_column_names, index=1, key='heatmap_y_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_heatmap_x_english = list(column_mapping.keys())[japanese_column_names.index(selected_heatmap_x_japanese)]
selected_heatmap_y_english = list(column_mapping.keys())[japanese_column_names.index(selected_heatmap_y_japanese)]

# データフレームをピボットしてヒートマップ用のデータを準備
heatmap_df = df.groupby([selected_heatmap_x_english, selected_heatmap_y_english]).size().reset_index(name='counts')
heatmap_df_pivot = heatmap_df.pivot(index=selected_heatmap_y_english, columns=selected_heatmap_x_english, values='counts')

# ヒートマップを描画
fig = px.imshow(heatmap_df_pivot, labels=dict(x=column_mapping[selected_heatmap_x_english], y=column_mapping[selected_heatmap_y_english], color="Count"), x=heatmap_df_pivot.columns, y=heatmap_df_pivot.index, aspect="auto", title=f'{column_mapping[selected_heatmap_x_english]}と{column_mapping[selected_heatmap_y_english]}のヒートマップ')
st.plotly_chart(fig)
#############################################################################

st.markdown('<a name="section7"></a>', unsafe_allow_html=True)
st.title('Streamlitアプリのユーザー制御について')

st.markdown('''

『streamlitのアプリ内で、ユーザー制御を行い、ユーザーによって閲覧するデータを制限する方法を最新の情報をもとに調査してください。』

**ChatGPT**

『Streamlitにおけるユーザー制御とデータアクセスの制限には複数のアプローチがあります。以下に、最新情報に基づいた方法を紹介します。

### **1. Streamlitのセキュリティ機能**（[参考元資料](https://streamlit.io/security)）

Streamlitは、GitHubやGSuiteなどのSSOプロバイダーを通じたアクセスとサインインを行います。また、AES256を使用してセンシティブな顧客データ（例：シークレット、認証トークン）を暗号化し、データを保護します。さらに、権限とロールベースのアクセスコントロールを通じて、GitHubで割り当てられた権限を引き継ぎ、アプリの変更やデプロイが可能なユーザーを制限します。

### **2. Streamlit-Authenticator**（[参考元資料](https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/)）

Streamlit-Authenticatorは、ユーザー認証をアプリに追加するためのコンポーネントです。YAMLファイルにユーザー情報を定義し、ハッシュ化されたパスワードとともに認証オブジェクトを作成します。ログインウィジェットをレンダリングして認証状態を管理し、ユーザー名に基づいて個々のユーザーに特化した体験を提供することが可能です。

### **3. Djangoを使用したユーザー制御**（[参考元資料](https://www.the-analytics.club/streamlit-advanced-authentication/)）

StreamlitアプリにDjangoの認証システムを組み込むことで、より強力なユーザー管理とデータアクセス制御を実現します。Djangoの管理インターフェイスを利用して、新しいユーザーやユーザーグループの作成、グループメンバーシップの管理ができます。また、特定のダッシュボードへのアクセスをユーザーのロールに基づいて制限することができます。

### **4. 単純なパスワードベースの認証**（[参考元資料](https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso)）

**`.streamlit/secrets.toml`**ファイルにパスワードを設定し、Streamlitアプリでこのパスワードを要求することで、簡易的なユーザー認証を実現することも可能です。クラウドにデプロイされたアプリでは、Streamlitのシークレット管理機能を利用して、このパスワードをアプリに渡します。

### **5. st.experimental_userを使ったユーザー情報の取得**（[参考元資料](https://docs.streamlit.io/library/api-reference/personalization/st.experimental_user)）

**`st.experimental_user`**は、現在のユーザーに関する情報をアクセスするための読み取り専用の辞書ライクなオブジェクトです。これを利用することで、ログインしているユーザーのメールアドレスに基づいてアプリのコンテンツをカスタマイズすることができます。ただし、この機能は実験的なものであり、APIは変更される可能性があることに注意が必要です。』
            ''')


# .streamlit/secrets.toml
# openai_api_key = "YOUR_OPENAI_API_KEY"

st.markdown('<a name="section8"></a>', unsafe_allow_html=True)

# APIキーの設定
openai.api_key = OPENAI_API_KEY

st.title("ChatGPT Demo")

# ユーザーからの入力を受け取る
user_input = st.text_input("あなたの質問を入力してください:")

# 「送信」ボタンが押されたら応答を取得する
if st.button("送信"):
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",  # 使用するモデルを指定
        messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                    {"role": "user", "content": user_input}],
    )
    # 応答を表示
    st.text_area("ChatGPTの応答:", value=response['choices'][0]['message']['content'], height=200, max_chars=None, key=None)




st.markdown('<a name="section9"></a>', unsafe_allow_html=True)
st.title('妄想')

st.markdown('''
Azure上に売上データ等で、RAGを構築してGPT(AzureOpenAI)に参照させて、（かつ、AutoGenとかでGPT同士の会話を見ながら、簡易的なデータ分析ができる？？（←現状、コストと得られるものが見合わないかも。。）
加えて、autoGenでプログラミングのお願いをすると、openinterpreterのように、ローカル上でパッケージ等をインストールするので、環境をめちゃくちゃにされる可能性。ユーザーに使用させるのには向かないかも。
''')


######################AutoGenを利用#########################

st.markdown('<a name="section10"></a>', unsafe_allow_html=True)

# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# # OAI_CONFIG_LIST.jsonファイルに設定を記述

# # Load LLM inference endpoints from an env variable or a file
# # See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
# # and OAI_CONFIG_LIST_sample.json
# config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
# assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False}) # IMPORTANT: set to True to run code in docker, recommended
# user_proxy.initiate_chat(assistant, message="NVIDIAのここ5年間の株価をプロットします。")
# # This initiates an automated chat between the two agents to solve the task
# import streamlit as st
# from autogen import AssistantAgent, UserProxyAgent

# # Initialize your AutoGen setup
# # config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
# assistant = AssistantAgent("assistant", llm_config={"config_list": [{"model": "gpt-4", "api_key": OPENAI_API_KEY}, {"model": "gpt-3.5-turbo", "api_key": OPENAI_API_KEY}]})
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})  # IMPORTANT: set to True to run code in docker, recommended

# def initiate_chat(message):
#     # This function will handle the chat initiation and return the assistant's response
#     # Note: This is a placeholder function. You'll need to adapt it to your actual AutoGen setup and ensure it captures and returns the assistant's response correctly.
#     response = "This is where you'll display the assistant's response."
#     return response

# # Streamlit UI
# st.title("AutoGen Integration Example")

# # User input
# user_message = st.text_input("Enter your message:", "")

# # Button to initiate chat
# if st.button("Send"):
#     # Initiate chat with the assistant and capture the response
#     response = initiate_chat(user_message)
    
#     # Display the response
#     st.text_area("Assistant's Response:", value=response, height=300)

# # Note: This is a simplified example. The actual implementation of the initiate_chat function
# # will depend on how you've set up your AutoGen configuration and how you handle the chat logic.


###############################サイドバーにソースコードを表示################################
code = '''
import snowflake.connector
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import openai

load_dotenv()

# 環境変数ファイルの読み込み
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
account = os.getenv('SNOWFLAKE_ACCOUNT')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
database = os.getenv('SNOWFLAKE_DATABASE')
schema = os.getenv('SNOWFLAKE_SCHEMA')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Streamlitアプリのタイトル
st.title('Snowflake Data Analysis App')

st.text("""
【アプリ概要】
Snowflake上のデータ（ORDERSテーブル）を取得し、ユーザーが選択したカラムを多様なグラフで表示する
""")

# Markdownを使用してリンクを表示
st.markdown('[今回のLTのきっかけ記事（NTTドコモがStreamlitを社内導入）](https://news.yahoo.co.jp/articles/624de9b79dd9e53164ece15231d6e524a36d8ad4)')

st.markdown('[ソースコード](https://github.com/seiji0906/snowflake-streamlit)')
st.markdown('[サンプルデータ元](https://www.kaggle.com/datasets/kyanyoga/sample-sales-data?resource=download)')

st.markdown('[Streamlit公式ページ](https://streamlit.io)')
st.markdown('[Streamlit Cheat Sheet](https://cheat-sheet.streamlit.app)')

# 目次
st.markdown("""
# 目次
1. [散布図](#section1)
2. [ヒストグラム](#section2)
3. [箱ひげ図](#section3)
4. [棒グラフ](#section4)
5. [円グラフ](#section5)
6. [ヒートマップ](#section6)
7. [Streamlitアプリのユーザー制御について](#section7)
8. [ChatGPT](#section8)
9. [妄想](#section9)
10. [AutoGen](#section10)
""", unsafe_allow_html=True)


###### 文字列表示系
# st.text('Fixed width text')
# st.markdown('_Markdown_') # see #*
# st.caption('Balloons. Hundreds of them...')
# st.latex(r''' e^{i\pi} + 1 = 0 ''')
# st.write('Most objects') # df, err, func, keras!
# st.write(['st', 'is <', 3]) # see *
# st.title('My title')
# st.header('My header')
# st.subheader('My sub')
# st.code('for i in range(8): foo()')

###################snowflakeへ接続########################
# Snowflakeへの接続情報
conn_info = {
    'user': user,
    'password': password,
    'account': account,
    'warehouse': warehouse,
    'database': database,
    'schema': schema
}

# Snowflakeに接続
conn = snowflake.connector.connect(**conn_info)

    # SQLクエリの実行とDataFrameへの読み込み
sql_query = "SELECT * FROM orders"
df = pd.read_sql(sql_query, conn)

# 接続を閉じる
conn.close()
#########################################################


#####################ORDERSテーブルのカラム名とその日本語のマッピング#######################
# 英語のカラム名とそれに対応する日本語訳をマッピングしたオブジェクト
column_mapping = {
    "ORDERNUMBER": "注文番号",
    "QUANTITYORDERED": "注文数量",
    "PRICEEACH": "単価",
    "ORDERLINENUMBER": "注文行番号",
    "SALES": "売上",
    "ORDERDATE": "注文日（データ空です。）",
    "STATUS": "ステータス",
    "QTR_ID": "四半期ID",
    "MONTH_ID": "月ID",
    "YEAR_ID": "年ID",
    "PRODUCTLINE": "製品ライン",
    "MSRP": "希望小売価格",
    "PRODUCTCODE": "製品コード",
    "CUSTOMERNAME": "顧客名",
    "PHONE": "電話番号",
    "ADDRESSLINE1": "住所1",
    "ADDRESSLINE2": "住所2",
    "CITY": "市区町村",
    "STATE": "都道府県",
    "POSTALCODE": "郵便番号",
    "COUNTRY": "国",
    "TERRITORY": "地域",
    "CONTACTLASTNAME": "担当者姓",
    "CONTACTFIRSTNAME": "担当者名",
    "DEALSIZE": "取引規模"
}
############################################################################################



############################### 散布図 #####################################
st.markdown('<a name="section1"></a>', unsafe_allow_html=True)
st.header('散布図')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# 日本語のカラム名のリストを選択肢として渡す
japanese_column_names = list(column_mapping.values())
selected_x_japanese = st.selectbox('X軸に使用するカラムを選択してください', japanese_column_names, index=0, key='scatter_x')
selected_y_japanese = st.selectbox('Y軸に使用するカラムを選択してください', japanese_column_names, index=1, key='scatter_y')

# 選択された日本語名から英語のカラム名を逆引き
selected_x_english = list(column_mapping.keys())[japanese_column_names.index(selected_x_japanese)]
selected_y_english = list(column_mapping.keys())[japanese_column_names.index(selected_y_japanese)]


# 散布図を表示
fig = px.scatter(df, x=selected_x_english, y=selected_y_english, title=f'{column_mapping[selected_x_english]} vs {column_mapping[selected_y_english]}')
st.plotly_chart(fig)
############################################################################


#############################ヒストグラム##################################
st.markdown('<a name="section2"></a>', unsafe_allow_html=True)
# ヒストグラムセクション
st.header('ヒストグラム')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# ヒストグラムのカラム選択。キーを使って散布図のセレクトボックスと区別します。
selected_histogram_japanese = st.selectbox('ヒストグラムに使用するカラムを選択してください', japanese_column_names, index=0, key='histogram_select')
selected_histogram_english = list(column_mapping.keys())[japanese_column_names.index(selected_histogram_japanese)]

# 選択されたカラムに基づいてヒストグラムを描画
fig = px.histogram(df, x=selected_histogram_english, title=f'{column_mapping[selected_histogram_english]}のヒストグラム')
st.plotly_chart(fig)
############################################################################

##################################箱ひげ図##################################
st.markdown('<a name="section3"></a>', unsafe_allow_html=True)
# 箱ひげ図セクション
st.header('箱ひげ図')

# st.expanderを使用してカラム名マッピングを閉じた状態で表示
with st.expander("カラム名マッピングを表示", expanded=False):
    st.write(column_mapping)

# 箱ひげ図のカラム選択。キーを使って他のセレクトボックスと区別します。
selected_boxplot_japanese = st.selectbox('箱ひげ図に使用するカラムを選択してください', japanese_column_names, index=0, key='boxplot_select')
selected_boxplot_english = list(column_mapping.keys())[japanese_column_names.index(selected_boxplot_japanese)]

# 選択されたカラムに基づいて箱ひげ図を描画
fig = px.box(df, y=selected_boxplot_english, title=f'{column_mapping[selected_boxplot_english]}の箱ひげ図')
st.plotly_chart(fig)
#############################################################################

####################################棒グラフ#################################
st.markdown('<a name="section4"></a>', unsafe_allow_html=True)
# 棒グラフセクション
st.header('棒グラフ')
# 棒グラフのカテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_bar_category_japanese = st.selectbox('棒グラフのカテゴリとして使用するカラムを選択してください', japanese_column_names, index=0, key='bar_category_select')
# 棒グラフの値カラム選択
selected_bar_value_japanese = st.selectbox('棒グラフの値として使用するカラムを選択してください', japanese_column_names, index=1, key='bar_value_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_bar_category_english = list(column_mapping.keys())[japanese_column_names.index(selected_bar_category_japanese)]
selected_bar_value_english = list(column_mapping.keys())[japanese_column_names.index(selected_bar_value_japanese)]

# 選択されたカラムに基づいて棒グラフを描画
fig = px.bar(df, x=selected_bar_category_english, y=selected_bar_value_english, title=f'{column_mapping[selected_bar_category_english]}による{column_mapping[selected_bar_value_english]}の棒グラフ')
st.plotly_chart(fig)
#############################################################################

#####################################円グラフ#################################
st.markdown('<a name="section5"></a>', unsafe_allow_html=True)
# 円グラフセクション
st.header('円グラフ')
# 円グラフのカテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_pie_chart_japanese = st.selectbox('円グラフに使用するカテゴリカラムを選択してください', japanese_column_names, index=0, key='pie_chart_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_pie_chart_english = list(column_mapping.keys())[japanese_column_names.index(selected_pie_chart_japanese)]

# 選択されたカラムに基づいて円グラフを描画
fig = px.pie(df, names=selected_pie_chart_english, title=f'{column_mapping[selected_pie_chart_english]}の円グラフ')
st.plotly_chart(fig)
###############################################################################


###################################ヒートマップ#################################
st.markdown('<a name="section6"></a>', unsafe_allow_html=True)
# ヒートマップセクション
st.header('ヒートマップ')
# ヒートマップのX軸カテゴリカラム選択。キーを使って他のセレクトボックスと区別します。
selected_heatmap_x_japanese = st.selectbox('ヒートマップのX軸に使用するカテゴリカラムを選択してください', japanese_column_names, index=0, key='heatmap_x_select')
# ヒートマップのY軸カテゴリカラム選択。
selected_heatmap_y_japanese = st.selectbox('ヒートマップのY軸に使用するカテゴリカラムを選択してください', japanese_column_names, index=1, key='heatmap_y_select')

# 選択された日本語名から英語のカラム名を逆引き
selected_heatmap_x_english = list(column_mapping.keys())[japanese_column_names.index(selected_heatmap_x_japanese)]
selected_heatmap_y_english = list(column_mapping.keys())[japanese_column_names.index(selected_heatmap_y_japanese)]

# データフレームをピボットしてヒートマップ用のデータを準備
heatmap_df = df.groupby([selected_heatmap_x_english, selected_heatmap_y_english]).size().reset_index(name='counts')
heatmap_df_pivot = heatmap_df.pivot(index=selected_heatmap_y_english, columns=selected_heatmap_x_english, values='counts')

# ヒートマップを描画
fig = px.imshow(heatmap_df_pivot, labels=dict(x=column_mapping[selected_heatmap_x_english], y=column_mapping[selected_heatmap_y_english], color="Count"), x=heatmap_df_pivot.columns, y=heatmap_df_pivot.index, aspect="auto", title=f'{column_mapping[selected_heatmap_x_english]}と{column_mapping[selected_heatmap_y_english]}のヒートマップ')
st.plotly_chart(fig)
#############################################################################

st.markdown('<a name="section7"></a>', unsafe_allow_html=True)
st.title('Streamlitアプリのユーザー制御について')

st.markdown('''

『streamlitのアプリ内で、ユーザー制御を行い、ユーザーによって閲覧するデータを制限する方法を最新の情報をもとに調査してください。』

**ChatGPT**

『Streamlitにおけるユーザー制御とデータアクセスの制限には複数のアプローチがあります。以下に、最新情報に基づいた方法を紹介します。

### **1. Streamlitのセキュリティ機能**（[参考元資料](https://streamlit.io/security)）

Streamlitは、GitHubやGSuiteなどのSSOプロバイダーを通じたアクセスとサインインを行います。また、AES256を使用してセンシティブな顧客データ（例：シークレット、認証トークン）を暗号化し、データを保護します。さらに、権限とロールベースのアクセスコントロールを通じて、GitHubで割り当てられた権限を引き継ぎ、アプリの変更やデプロイが可能なユーザーを制限します。

### **2. Streamlit-Authenticator**（[参考元資料](https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/)）

Streamlit-Authenticatorは、ユーザー認証をアプリに追加するためのコンポーネントです。YAMLファイルにユーザー情報を定義し、ハッシュ化されたパスワードとともに認証オブジェクトを作成します。ログインウィジェットをレンダリングして認証状態を管理し、ユーザー名に基づいて個々のユーザーに特化した体験を提供することが可能です。

### **3. Djangoを使用したユーザー制御**（[参考元資料](https://www.the-analytics.club/streamlit-advanced-authentication/)）

StreamlitアプリにDjangoの認証システムを組み込むことで、より強力なユーザー管理とデータアクセス制御を実現します。Djangoの管理インターフェイスを利用して、新しいユーザーやユーザーグループの作成、グループメンバーシップの管理ができます。また、特定のダッシュボードへのアクセスをユーザーのロールに基づいて制限することができます。

### **4. 単純なパスワードベースの認証**（[参考元資料](https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso)）

**`.streamlit/secrets.toml`**ファイルにパスワードを設定し、Streamlitアプリでこのパスワードを要求することで、簡易的なユーザー認証を実現することも可能です。クラウドにデプロイされたアプリでは、Streamlitのシークレット管理機能を利用して、このパスワードをアプリに渡します。

### **5. st.experimental_userを使ったユーザー情報の取得**（[参考元資料](https://docs.streamlit.io/library/api-reference/personalization/st.experimental_user)）

**`st.experimental_user`**は、現在のユーザーに関する情報をアクセスするための読み取り専用の辞書ライクなオブジェクトです。これを利用することで、ログインしているユーザーのメールアドレスに基づいてアプリのコンテンツをカスタマイズすることができます。ただし、この機能は実験的なものであり、APIは変更される可能性があることに注意が必要です。』
            ''')


# .streamlit/secrets.toml
# openai_api_key = "YOUR_OPENAI_API_KEY"

st.markdown('<a name="section8"></a>', unsafe_allow_html=True)

# APIキーの設定
openai.api_key = OPENAI_API_KEY

st.title("ChatGPT Demo")

# ユーザーからの入力を受け取る
user_input = st.text_input("あなたの質問を入力してください:")

# 「送信」ボタンが押されたら応答を取得する
if st.button("送信"):
    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",  # 使用するモデルを指定
        messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                    {"role": "user", "content": user_input}],
    )
    # 応答を表示
    st.text_area("ChatGPTの応答:", value=response['choices'][0]['message']['content'], height=200, max_chars=None, key=None)




st.markdown('<a name="section9"></a>', unsafe_allow_html=True)
st.title('妄想')

st.markdown('''
Azure上に売上データ等で、RAGを構築してGPT(AzureOpenAI)に参照させて、（かつ、AutoGenとかでGPT同士の会話を見ながら、簡易的なデータ分析ができる？？（←現状、コストと得られるものが見合わないかも。。）
加えて、autoGenでプログラミングのお願いをすると、openinterpreterのように、ローカル上でパッケージ等をインストールするので、環境をめちゃくちゃにされる可能性。ユーザーに使用させるのには向かないかも。
''')


######################AutoGenを利用#########################

st.markdown('<a name="section10"></a>', unsafe_allow_html=True)

# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# # OAI_CONFIG_LIST.jsonファイルに設定を記述

# # Load LLM inference endpoints from an env variable or a file
# # See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
# # and OAI_CONFIG_LIST_sample.json
# config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
# assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False}) # IMPORTANT: set to True to run code in docker, recommended
# user_proxy.initiate_chat(assistant, message="NVIDIAのここ5年間の株価をプロットします。")
# # This initiates an automated chat between the two agents to solve the task
# import streamlit as st
# from autogen import AssistantAgent, UserProxyAgent

# # Initialize your AutoGen setup
# # config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
# assistant = AssistantAgent("assistant", llm_config={"config_list": [{"model": "gpt-4", "api_key": OPENAI_API_KEY}, {"model": "gpt-3.5-turbo", "api_key": OPENAI_API_KEY}]})
# user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})  # IMPORTANT: set to True to run code in docker, recommended

# def initiate_chat(message):
#     # This function will handle the chat initiation and return the assistant's response
#     # Note: This is a placeholder function. You'll need to adapt it to your actual AutoGen setup and ensure it captures and returns the assistant's response correctly.
#     response = "This is where you'll display the assistant's response."
#     return response

# # Streamlit UI
# st.title("AutoGen Integration Example")

# # User input
# user_message = st.text_input("Enter your message:", "")

# # Button to initiate chat
# if st.button("Send"):
#     # Initiate chat with the assistant and capture the response
#     response = initiate_chat(user_message)
    
#     # Display the response
#     st.text_area("Assistant's Response:", value=response, height=300)

# # Note: This is a simplified example. The actual implementation of the initiate_chat function
# # will depend on how you've set up your AutoGen configuration and how you handle the chat logic.
'''
st.sidebar.code(code, language='python')
