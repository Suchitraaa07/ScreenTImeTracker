import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MyTracker", layout="wide")

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
    color: white !important;
}
            
section[data-testid="stSidebar"] a:hover {
    background-color: white;
    color: #1e293b !important;
}

section[data-testid="stSidebar"] a[aria-current="page"] {
    background-color: #2563eb;
    background-color: #ffffff;
    color: white !important;
}
            
.sidebar-item {
    padding: 10px 16px;
    color: #cbd5ff5;
    border-radius: 8px;
    margin-bottom: 6px;
    font-weight: 500;
}
.sidebar-item.active {
    background: #2563eb;
    color: white;
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


# ---------------- LOAD DATA ----------------
conn = get_connection()
df = pd.read_sql("SELECT * FROM tracker_db", conn)
conn.close()

df["start_time"] = pd.to_datetime(df["start_time"])
df["end_time"] = pd.to_datetime(df["end_time"])

# ---------------- KPIs ----------------
total_sec = df["duration"].sum()
total_time = f"{int(total_sec//3600):02d}h {int((total_sec%3600)//60):02d}m"
sessions = len(df)
top_app = df.groupby("event")["duration"].sum().idxmax()

df["hour"] = df["start_time"].dt.hour
peak_hour = df.groupby("hour")["duration"].sum().idxmax()
peak_hour_label = f"{peak_hour}:00 – {peak_hour+1}:00"

st.title("🎯 MyTracker Dashboard")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='kpi kpi-blue'><div class='kpi-title'>Total Time</div><div class='kpi-value'>{total_time}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='kpi kpi-purple'><div class='kpi-title'>Total Sessions</div><div class='kpi-value'>{sessions}</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='kpi kpi-green'><div class='kpi-title'>Top App</div><div class='kpi-value'>{top_app}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='kpi kpi-orange'><div class='kpi-title'>Most Active</div><div class='kpi-value'>{peak_hour_label}</div></div>", unsafe_allow_html=True)

# ---------------- ROW 1 ----------------
l1, r1 = st.columns([2, 1])

# ---- Usage Timeline (SCATTER) ----
df["bubble_size"] = df["duration"].apply(lambda x: min(max(x * 0.02, 6), 22))

scatter_fig = px.scatter(
    df,
    x="start_time",
    y="event",
    size="bubble_size",
    color="event",
    size_max=22
)

scatter_fig.update_layout(
    height=360,
    showlegend=False,
    margin=dict(l=220, r=20, t=30, b=20),
    xaxis_title="Time",
    yaxis_title=""
)

with l1:
    st.markdown("<div class='card'><h4>Usage Timeline</h4>", unsafe_allow_html=True)
    st.plotly_chart(scatter_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Donut Chart ----
donut_df = df.groupby("event", as_index=False)["duration"].sum()
donut_fig = px.pie(
    donut_df,
    names="event",
    values="duration",
    hole=0.55
)
donut_fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)
donut_fig.update_layout(
    height=420,
    width=420,              # 🔥 key line
    showlegend=False,       # legend eats space
    margin=dict(t=20, b=20, l=20, r=20)
)

with r1:
    st.markdown("<div class='card'><h4>Top Applications</h4>", unsafe_allow_html=True)
    st.plotly_chart(donut_fig, use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------- ROW 2 ----------------
l2, r2 = st.columns(2)

# ---- Screen Time Overview (FORCE 7 DAYS) ----
df["date"] = df["start_time"].dt.date
df["day"] = df["start_time"].dt.day_name()

# get last 7 calendar days
last_7_days = pd.date_range(
    end=df["start_time"].max().date(),
    periods=7
)

screen_df = (
    df.groupby(df["start_time"].dt.date)["duration"]
    .sum()
    .reindex(last_7_days.date, fill_value=0)
    .reset_index()
)

screen_df.columns = ["date", "duration"]
screen_df["day"] = pd.to_datetime(screen_df["date"]).dt.day_name()

screen_fig = px.bar(
    screen_df,
    x="day",
    y="duration",
    text=screen_df["duration"].apply(
        lambda x: f"{int(x//3600)}h" if x > 0 else ""
    )
)

screen_fig.update_layout(
    height=320,
    yaxis_title="Total Screen Time (sec)",
    xaxis_title="Day",
    showlegend=False,
    margin=dict(t=30, b=20, l=40, r=20)
)

screen_fig.update_traces(textposition="outside")


# ---- Heatmap ----
heat_df = df.groupby(["day", "hour"])["duration"].sum().reset_index()

heatmap_fig = px.density_heatmap(
    heat_df,
    x="hour",
    y="day",
    z="duration",
    color_continuous_scale="YlOrRd"
)

heatmap_fig.update_layout(height=320)

with r2:
    st.markdown("<div class='card'><h4>Hourly Activity Heatmap</h4>", unsafe_allow_html=True)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ROW 3 ----------------
t1, t2 = st.columns([3, 1])

with t1:
    st.markdown("<div class='card'><h4>Recent Activities</h4>", unsafe_allow_html=True)
    st.dataframe(df[["event","start_time","end_time","duration"]], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with t2:
    st.markdown(f"""
    <div class="card">
        <h4>Usage Summary</h4>
        <h2>{total_time}</h2>
        <p>Avg Daily Usage</p>
        <hr>
        <h3>{int(df["duration"].max()//3600)}h {int((df["duration"].max()%3600)//60)}m</h3>
        <p>Longest Session</p>
    </div>
    """, unsafe_allow_html=True)


with l2:
    st.markdown("<div class='card'><h4>Screen Time Overview</h4>", unsafe_allow_html=True)
    st.plotly_chart(screen_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)