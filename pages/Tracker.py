import pandas as pd
import streamlit as st
from db import get_connection
import time
import pygetwindow as gw
from datetime import datetime

st.set_page_config(
    page_title="MyTracker",
    page_icon=":bar_chart:",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#f8fafc,#eef2ff);
}

/* ---- SIDEBAR (UNCHANGED) ---- */
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

/* ---- CARDS ---- */
.card {
    background: linear-gradient(180deg,#ffffff,#f8fafc);
    padding: 1.6rem;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* ---- SECTION HEADERS ---- */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.8rem;
}

.section-divider {
    height: 1px;
    background: linear-gradient(90deg,#c7d2fe,#ffffff);
    margin: 1rem 0 1.4rem 0;
}

/* ---- METRICS ---- */
.metric {
    font-size: 1.7rem;
    font-weight: 800;
    color: #2563eb;
}
.label {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 4px;
}

/* ---- BUTTONS ---- */
button {
    border-radius: 14px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

if "tracking_active" not in st.session_state:
    st.session_state.tracking_active = False
if "previous_window" not in st.session_state:
    st.session_state.previous_window = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None
if "switch_count" not in st.session_state:
    st.session_state.switch_count = 0

st.title("⏱️ MyTracker")

st.markdown(
    "<p style='color:#475569;margin-top:-8px;'>Lightweight desktop activity tracking</p>",
    unsafe_allow_html=True
)

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Tracking Controls</div>", unsafe_allow_html=True)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    if st.button("▶ Start Tracking", use_container_width=True):
        st.session_state.tracking_active = True
        st.session_state.previous_window = None
        st.session_state.start_time = None
        st.session_state.session_start_time = datetime.now()
        st.session_state.switch_count = 0

with c2:
    if st.button("⏹ Stop Tracking", use_container_width=True):
        st.session_state.tracking_active = False

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.tracking_active:
    window = gw.getActiveWindow()
    current_title = window.title if window else "Unknown"

    if st.session_state.previous_window is None:
        st.session_state.previous_window = current_title
        st.session_state.start_time = datetime.now()

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

        st.session_state.previous_window = current_title
        st.session_state.start_time = datetime.now()
        st.session_state.switch_count += 1

    elapsed = datetime.now() - st.session_state.session_start_time

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Live Session</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)

    m1.markdown(
        f"<div class='metric'>{str(elapsed).split('.')[0]}</div><div class='label'>Session Time</div>",
        unsafe_allow_html=True
    )

    m2.markdown(
        f"<div class='metric'>{st.session_state.switch_count}</div><div class='label'>Window Switches</div>",
        unsafe_allow_html=True
    )

    conn = get_connection()
    temp_df = pd.read_sql(
        """
        SELECT event, SUM(duration) as total
        FROM tracker_db
        WHERE start_time >= %s
        GROUP BY event
        ORDER BY total DESC
        LIMIT 1
        """,
        conn,
        params=(st.session_state.session_start_time,),
    )
    conn.close()

    top_session_app = temp_df.iloc[0]["event"] if not temp_df.empty else "—"

    m3.markdown(
        f"<div class='metric'>{top_session_app[:18]}</div><div class='label'>Top App (Session)</div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()

if not st.session_state.tracking_active and st.session_state.session_start_time:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Session Summary</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT *
        FROM tracker_db
        WHERE start_time >= %s
        ORDER BY start_time
        """,
        conn,
        params=(st.session_state.session_start_time,),
    )
    conn.close()

    if not df.empty:
        st.dataframe(
            df[["event", "start_time", "end_time", "duration"]],
            use_container_width=True,
            height=300
        )
    else:
        st.info("No activity recorded in this session.")

    st.markdown("</div>", unsafe_allow_html=True)