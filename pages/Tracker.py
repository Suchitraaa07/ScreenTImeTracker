import pandas as pd
import streamlit as st
from db import get_connection
import time
import plotly.express as px
import pygetwindow as gw
from datetime import datetime

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

# ---------------- SESSION STATE INIT ----------------
if "tracking_active" not in st.session_state:
    st.session_state.tracking_active = False

if "previous_window" not in st.session_state:
    st.session_state.previous_window = None

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None

# ---------------- BUTTONS ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Start"):
        st.session_state.tracking_active = True
        st.session_state.previous_window = None
        st.session_state.start_time = None
        st.session_state.session_start_time = datetime.now()

with col2:
    if st.button("Stop"):
        st.session_state.tracking_active = False

# ---------------- TRACKING LOGIC ----------------
if st.session_state.tracking_active:
    st.markdown("### ⏳ Tracking started...")

    window = gw.getActiveWindow()
    current_title = window.title if window else "Unknown"

    # First window → initialize only
    if st.session_state.previous_window is None:
        st.session_state.previous_window = current_title
        st.session_state.start_time = datetime.now()

    # Window changed → insert previous window record
    elif current_title != st.session_state.previous_window:
        end_time = datetime.now()
        duration = (end_time - st.session_state.start_time).total_seconds()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO tracker_db (event, start_time, end_time, duration)
            VALUES (%s, %s, %s, %s)
            """,
            (
                st.session_state.previous_window,
                st.session_state.start_time,
                end_time,
                duration,
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

        # Update state for new window
        st.session_state.previous_window = current_title
        st.session_state.start_time = datetime.now()

    # Rerun every second while tracking
    time.sleep(1)
    st.rerun()

# ---------------- DISPLAY AFTER STOP (SESSION ONLY) ----------------
if not st.session_state.tracking_active and st.session_state.session_start_time:
    st.markdown("### ⏹️ Tracking stopped")

    conn = get_connection()
    query = """
    SELECT *
    FROM tracker_db
    WHERE start_time >= %s
    ORDER BY start_time
    """
    df = pd.read_sql(query, conn, params=(st.session_state.session_start_time,))
    conn.close()

    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No activity recorded in this session.")
