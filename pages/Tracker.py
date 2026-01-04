import pandas as pd
import streamlit as st
from db import get_connection
from timefetch import fetch_window_times
import time
import plotly.express as px

st.set_page_config(page_title="MyTracker", page_icon=":bar_chart:", layout="centered")

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1e293b,#0f172a);
}
 
section[data-testid="stSidebar"] a {
    font-size: 15px;
    padding: 10px 16px;
    border-radius: 10px;
    color: white;
}

section[data-testid="stSidebar"] a[aria-current="page"] {
    background-color: white;
    color: #1e293b !important;
}

section[data-testid="stSidebar"] a:hover {
    background-color: white;
    color: #1e293b !important;
}

.sidebar-item {
    padding: 10px 16px;
    color: #fffff;
    border-radius: 8px;
    margin-bottom: 6px;
    font-weight: 500;
}
.sidebar-item.active {
    background: #2563eb;
    color: white !important;
}
.kpi {
    min-height: 110px;
    max-height: 110px;
    overflow: hidden;
}

.card {
    background: white;
    padding: 1.2rem;
    border-radius: 14px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.08);
}

.kpi {
    color: white;
    padding: 1.4rem;
    border-radius: 16px;
    font-weight: 600;
}

.kpi-blue { background: linear-gradient(135deg,#3b82f6,#2563eb); }
.kpi-purple { background: linear-gradient(135deg,#8b5cf6,#7c3aed); }
.kpi-green { background: linear-gradient(135deg,#22c55e,#16a34a); }
.kpi-orange { background: linear-gradient(135deg,#fb923c,#f97316); }

.kpi-title { font-size: 0.9rem; opacity: 0.9; }
.kpi-value { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

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