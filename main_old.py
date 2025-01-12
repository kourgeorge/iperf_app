import streamlit as st
import pandas as pd
import time
import threading
from datetime import datetime
from iperf3 import Client
import os


# Streamlit UI
st.title("iPerf3 Multi-Server Performance Monitor")

# File paths
servers_file = "servers.csv"
servers_df = load_servers(servers_file)

# Editable table
st.header("Server Configuration")
updated_servers_df = st.experimental_data_editor(servers_df, use_container_width=True)

if st.button("Save Server Configuration"):
    save_servers(servers_file, updated_servers_df)
    st.success("Server configuration saved.")


# Display performance results
st.header("Performance Results")
for server in updated_servers_df.itertuples():
    if os.path.exists(server.results_file):
        df = pd.read_csv(server.results_file)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        mean_sent = df["sent_Mbps"].mean()
        mean_received = df["received_Mbps"].mean()

        st.subheader(f"Server: {server.hostname}")
        st.line_chart(df.set_index("timestamp")["sent_Mbps":"received_Mbps"])
        st.write(f"**Mean Sent Speed:** {mean_sent:.2f} Mbps")
        st.write(f"**Mean Received Speed:** {mean_received:.2f} Mbps")
    else:
        st.warning(f"No data available for {server.hostname}.")
