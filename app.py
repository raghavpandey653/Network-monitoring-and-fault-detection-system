import streamlit as st
import sqlite3
import pandas as pd
import subprocess
st.set_page_config(
    page_title="Network Monitoring System",
    page_icon="🌐",
    layout="wide"
)
st.title("Network Monitoring and Fault Detection System")
st.write("Monitor IP addresses and analyse network performance.")
if st.button("Run Monitoring"):
    with st.spinner("Monitoring network..."):
        result = subprocess.run(
            ["python", "multi_ip.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
    if result.returncode == 0:
        st.success("Monitoring completed successfully!")
        st.rerun()
    else:
        st.error("Monitoring failed")
        st.code(result.stderr)
connection = sqlite3.connect("network_monitor.db")
query = """
SELECT *
FROM monitoring_results
ORDER BY id DESC
"""
data = pd.read_sql_query(query, connection)
connection.close()
st.subheader("Latest Monitoring Status")
latest_data = data.drop_duplicates(
    subset="ip_address",
    keep="first"
)
st.dataframe(latest_data, use_container_width=True)
st.subheader("Packet Loss Percentage")
st.bar_chart(
    latest_data,
    x="ip_address",
    y="packet_loss"
)
st.subheader("Filter Monitoring Results")
ip_list = data["ip_address"].dropna().unique().tolist()
selected_ip = st.selectbox(
    "Select IP Address",
    ["All IPs"] + ip_list
)
if selected_ip == "All IPs":
    filtered_data = data
else:
    filtered_data = data[data["ip_address"] == selected_ip]
st.subheader("Filter by Network Status")
status_options = ["All Statuses"] + filtered_data["status"].dropna().unique().tolist()
selected_status = st.selectbox(
    "Select Status",
    status_options
)
if selected_status != "All Statuses":
    filtered_data = filtered_data[filtered_data["status"] == selected_status]
st.subheader("Monitoring History")
st.dataframe(filtered_data, use_container_width=True)
st.subheader("Network Status Overview")
online = len(filtered_data[filtered_data["status"] == "ONLINE"])
degraded = len(filtered_data[filtered_data["status"] == "DEGRADED"])
unreachable = len(filtered_data[filtered_data["status"] == "UNREACHABLE"])
col1, col2, col3 = st.columns(3)
col1.metric("Online", online)
col2.metric("Degraded", degraded)
col3.metric("Unreachable", unreachable)
st.subheader("Network Response Time")
chart_data = filtered_data[["id", "ip_address", "avg_rtt"]].dropna().copy()
chart_data["record"] = (
    chart_data["ip_address"] + " - #" +
    chart_data["id"].astype(str)
)
st.bar_chart(
    chart_data,
    x="record",
    y="avg_rtt"
)
st.subheader("Packet Loss Analysis")
loss_data = filtered_data[["id", "ip_address", "packet_loss"]].dropna().copy()
loss_data["record"] = (
    loss_data["ip_address"] + " - #" +
    loss_data["id"].astype(str)
)
st.bar_chart(
    loss_data,
    x="record",
    y="packet_loss"
)