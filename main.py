import streamlit as st
import pandas as pd
import time
from datetime import datetime
from iperf_utils import run_iperf_test
import threading

# Initialize global variables

# Helper function to periodically run iPerf tests
def periodic_iperf_tests(server_hostname, port, duration, interval, results_file):
    while True:
        result = run_iperf_test(server_hostname, port, duration)
        sent_Mbps = round(result.sent_Mbps)
        received_Mbps = round(result.received_Mbps)

        # Save the result to a CSV file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_data = {"timestamp": timestamp, "sent_Mbps": sent_Mbps, "received_Mbps": received_Mbps}
        df = pd.DataFrame([result_data])

        # Append to the CSV file
        if not pd.io.common.file_exists(results_file):
            df.to_csv(results_file, index=False)
        else:
            df.to_csv(results_file, mode="a", header=False, index=False)

        time.sleep(interval * 10)  # Sleep for the specified interval (in minutes)

# Streamlit UI
st.title("iPerf3 Server Performance Monitor")

server_hostname = st.text_input("Server Hostname", "avi.kour.me")
port = st.number_input("Port", min_value=1, max_value=65535, value=5201)
duration = st.slider("Test Duration (s)", min_value=1, max_value=60, value=10)
interval = st.slider("Test Interval (minutes)", min_value=1, max_value=60, value=5)

# Start periodic tests when the button is clicked
if st.button("Start Monitoring"):
    st.success("Monitoring started. Results will update periodically.")
    st.session_state["monitoring"] = True
    # Run the periodic tests in a background thread
    results_file = server_hostname.replace('.', '_') + ".csv"
    # Run the iPerf test
    st.session_state["results_file"] = results_file

    st.session_state["thread"] = threading.Thread(
        target=periodic_iperf_tests, args=(server_hostname, port, duration, interval, results_file), daemon=True
    )

    st.session_state["thread"].start()

# Display the graph
st.header("Performance Results")

if "monitoring" in st.session_state and st.session_state["monitoring"]:
    print (st.session_state)
    while True:
        if 'results_file' in st.session_state: #and pd.io.common.file_exists(results_file):
            results_file = st.session_state['results_file']
            df = pd.read_csv(results_file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            mean_sent = df["sent_Mbps"].mean()
            mean_received = df["received_Mbps"].mean()

            st.line_chart(df.set_index("timestamp")[["sent_Mbps", "received_Mbps"]])
            st.write(f"Mean Sent Speed: {mean_sent:.2f} Mbps")
            st.write(f"Mean Received Speed: {mean_received:.2f} Mbps")
        else:
            st.warning("No results available yet. Start monitoring to collect data.")

        # Refresh every 5 seconds
        time.sleep(5)
        st.rerun()