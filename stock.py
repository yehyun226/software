import os
import pandas as pd
import streamlit as st

data_dir = "data"
img_dir = os.path.join(data_dir, "image")
dates = [
    d for d in os.listdir(data_dir)
    if os.path.isdir(os.path.join(data_dir, d)) and d.isdigit()
]

image = {
    "삼성전자.csv": os.path.join(img_dir, "SAMSUNG.png"),
    "카카오.csv": os.path.join(img_dir, "KAKAO.png"),
    "LG전자.csv": os.path.join(img_dir, "LG.png"),
    "NAVER.csv": os.path.join(img_dir, "NAVER.png"),
    "SK.csv": os.path.join(img_dir, "SK.png")
}


st.title("주식 투자 도우미")
date = st.sidebar.selectbox("날짜 선택", ["20250929", "20250930", "20251001", "20251002", "20251010"])


date_path = os.path.join(data_dir, date)
stock = [f for f in os.listdir(date_path) if f.endswith(".csv")]

name = st.sidebar.selectbox("종목 선택", sorted(stock))
file_path = os.path.join(date_path, name)
df = pd.read_csv(file_path, encoding="utf-8")

if name in image and os.path.exists(image[name]):
    st.image(image[name], use_container_width=True)

time = "시간"
price = "주가"
volume = "순간거래량"
strength = "체결강도"

df = df.sort_values(by=time)
df = df[::-1].reset_index(drop=True)
df["time"] = df.index

tab1, tab2, tab3 = st.tabs(["주가", "순간거래량", "체결강도"])
tab1.write(f'시간별 {name}주가')
tab1.line_chart(df, x="시간", y="주가")
tab2.write(f'시간별 {name}순간거래량')
tab2.line_chart(df, x="시간", y="순간거래량")
tab3.write(f'시간별 {name}체결강도')
tab3.line_chart(df, x="시간", y="체결강도")
