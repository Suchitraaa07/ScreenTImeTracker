import pandas as pd
import streamlit as st
from db import get_connection
from timefetch import fetch_window_times
import time
import plotly.express as px

st.set_page_config(page_title="MyTracker", page_icon=":bar_chart:", layout="centered")
st.title("MyTracker")

duration = st.number_input("Enter duration in seconds:", min_value=1, value=10)

if st.button("Start Tracking"):

    st.markdown("Tracking started...")

    record = fetch_window_times(duration)
    conn = get_connection()
    cur = conn.cursor()

    query = ''' insert into tracker_db (event, start_time, end_time, duration) values (%s, %s, %s, %s) '''
    cur.executemany(query, record)
    conn.commit()

    query2 = ''' select * from tracker_db '''
    df = pd.read_sql(query2, conn)

    cur.close()
    conn.close()

    st.dataframe(df)

    record = pd.DataFrame(df, columns=["event", "start_time", "end_time", "duration"])