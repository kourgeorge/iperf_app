from datetime import time

import streamlit as st

import utils
from server import server_manager, server_tester
from utils import load_results


def streamlit_app():
    """Streamlit UI for iPerf3 Server Performance Monitoring."""
    st.title("iPerf3 Server Performance Monitor")

    # Sidebar for adding new servers
    st.sidebar.header("Configure Server")
    hostname = st.sidebar.text_input("Hostname", "")
    port = st.sidebar.number_input("Port", min_value=1024, max_value=65535, value=5201)
    duration = st.sidebar.number_input("Duration (seconds)", min_value=1, max_value=300, value=10)
    interval = st.sidebar.number_input("Interval (minutes)", min_value=1, max_value=60, value=5)
    add_server_button = st.sidebar.button("Add Server")

    # Add server functionality
    if add_server_button:
        if hostname and port and duration and interval:
            if not server_tester.test_server(hostname, port):
                st.sidebar.error(f"Failed to add server {hostname}:{port} - make sure the server is running iperf3")
            else:
                if server_manager.add_server(hostname, port, duration, interval):
                    st.sidebar.success(f"Server {hostname}:{port} added successfully!")

                else:
                    st.sidebar.error(f"Failed to add server {hostname}:{port}.")
        else:
            st.sidebar.error("Please fill all the fields correctly.")

    # Display existing servers
    server_df = server_manager.get_servers()
    if not server_df.empty:
        for _, server in server_df.iterrows():
            hostname = server["hostname"]
            results_file = server["results_file"]

            # Display server title with a remove button
            col1, col2 = st.columns([4, 1])  # Create two columns
            with col1:
                st.markdown(f"### Host: {hostname} (Port: {port}, Interval: {interval})")
            with col2:
                remove_button = st.button("Remove", key=f"remove_{hostname}_{port}")

            # Handle the remove button click
            if remove_button:
                server_manager.remove_server(hostname, port)
                server_tester.stop_testing(hostname, port)
                st.success(f"Server {hostname}:{port} removed successfully!")
                st.rerun()  # Refresh the page after removal

            result_data = load_results(results_file)

            if not result_data.empty:
                st.line_chart(
                    result_data.set_index("timestamp")[["sent_Mbps", "received_Mbps"]]
                )
            else:
                st.warning(f"No data available for {hostname}.")
    else:
        st.warning("No servers added yet. Add servers from the sidebar.")

    _, col2 = st.columns([5, 1])  # Create two columns
    with col2:
        refresh_button = st.button("Refresh", key="refresh", icon='🔄')

    # Handle the refresh button click
    if refresh_button:
        st.rerun()


if __name__ == "__main__":
    # Launch the Streamlit app
    streamlit_app()
