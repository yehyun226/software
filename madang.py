import streamlit as st
import pymysql
import pandas as pd
import time


dbConn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    port=st.secrets["mysql"]["port"],
    user=st.secrets["mysql"]["user"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)
cursor = dbConn.cursor(pymysql.cursors.DictCursor)


cursor = dbConn.cursor(pymysql.cursors.DictCursor)


def query(sql):
    cursor.execute(sql)
    return cursor.fetchall()


st.set_page_config(page_title="서점 관리시스템", layout="wide")
st.title("서점 관리 시스템")

menu = st.sidebar.radio("메뉴 선택", ["고객 조회", "도서 조회", "거래 입력", "고객 등록", "거래 요약"])

if menu == "고객 조회":
    name = st.text_input("🔍 고객 이름으로 검색", "")
    if len(name) > 0:
        sql = f"""
        SELECT c.custid, c.name, c.address, c.phone, b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON o.bookid = b.bookid
        WHERE c.name LIKE '%{name}%';
        """
        result = pd.DataFrame(query(sql))
        if not result.empty:
            st.success(f"총 {len(result)}건의 거래 내역이 검색되었습니다.")
            st.dataframe(result)
        else:
            st.warning("해당 고객의 거래 내역이 없습니다.")


elif menu == "도서 조회":
    st.subheader("서적 목록")
    result = pd.DataFrame(query("SELECT * FROM Book"))
    st.dataframe(result)

    st.subheader("수입 도서 (Imported_Book)")
    imported = pd.DataFrame(query("SELECT * FROM Imported_Book"))
    st.dataframe(imported)

elif menu == "거래 입력":
    st.subheader("거래 등록")

    # 고객 목록 불러오기
    customers = query("SELECT custid, name FROM Customer")
    cust_map = {f"{c['name']} ({c['custid']})": c['custid'] for c in customers}
    cust_select = st.selectbox("고객 선택", list(cust_map.keys()))

    # 도서 목록 불러오기
    books = query("SELECT bookid, bookname FROM Book")
    book_map = {f"{b['bookname']} ({b['bookid']})": b['bookid'] for b in books}
    book_select = st.selectbox("구매할 도서 선택", list(book_map.keys()))

    saleprice = st.number_input("판매 금액 입력", min_value=0, step=1000)

    if st.button("거래 입력"):
        custid = cust_map[cust_select]
        bookid = book_map[book_select]
        orderid = query("SELECT IFNULL(MAX(orderid),0)+1 AS nextid FROM Orders;")[0]['nextid']
        today = time.strftime('%Y-%m-%d')

        sql = f"""
        INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
        VALUES ({orderid}, {custid}, {bookid}, {saleprice}, '{today}');
        """
        cursor.execute(sql)
        dbConn.commit()
        st.success(f"거래가 등록되었습니다! (거래번호: {orderid})")

elif menu == "고객 등록":
    st.subheader("신규 고객 등록")
    name = st.text_input("고객 이름")
    address = st.text_input("주소")
    phone = st.text_input("전화번호 (예: 000-0000-0000)")
    if st.button("등록"):
        nextid = query("SELECT IFNULL(MAX(custid),0)+1 AS nextid FROM Customer;")[0]['nextid']
        sql = f"INSERT INTO Customer VALUES({nextid}, '{name}', '{address}', '{phone}');"
        cursor.execute(sql)
        dbConn.commit()
        st.success(f"신규 고객 '{name}'이(가) 등록되었습니다. (ID: {nextid})")

elif menu == "거래 요약":
    st.subheader("거래 통계 요약")
    sql = """
    SELECT c.name AS 고객명, COUNT(o.orderid) AS 거래수, SUM(o.saleprice) AS 총금액
    FROM Orders o
    JOIN Customer c ON o.custid = c.custid
    GROUP BY c.name
    ORDER BY 총금액 DESC;
    """
    df = pd.DataFrame(query(sql))
    st.dataframe(df)
