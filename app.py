import streamlit as st
from streamlit_autorefresh import st_autorefresh
import utils
from server import server_manager, server_tester
from utils import load_results
from streamlit_javascript import st_javascript


def streamlit_app():
    """Streamlit UI for iPerf3 Server Performance Monitoring."""
    # Fetch client timezone
    client_timezone = st_javascript("""await (async () => {
                const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                console.log(userTimezone)
                return userTimezone
    })().then(returnValue => returnValue)""")

    st.title("iPerf3 Server Performance Monitor")

    # Set the refresh interval (in milliseconds)
    refresh_interval = 5000  # 5 seconds
    count = st_autorefresh(interval=refresh_interval, limit=None, key="auto_refresh")

    # Sidebar for adding new servers
    st.sidebar.header("Configure Server")
    hostname = st.sidebar.text_input("Hostname", "")
    port = st.sidebar.number_input("Port", min_value=1024, max_value=65535, value=5201)
    duration = st.sidebar.number_input("Duration (seconds)", min_value=1, max_value=50, value=10)
    interval = st.sidebar.number_input("Interval (minutes)", min_value=1, max_value=60, value=5)
    add_server_button = st.sidebar.button("Add Server")

    # Add server functionality
    if add_server_button:
        if hostname and port and duration and interval:
            # if test_server_port(hostname, port):
            #     st.sidebar.success(f"Could reach {hostname}:{port}.")
            success, error = server_tester.validate_iperf_on_server(hostname, port)
            if not success:
                st.sidebar.error(f"Failed to add server {hostname}:{port}. Error: {error}.")
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
                st.markdown(f"### {hostname} (Port: {port}, Interval: {interval})")
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
                # Convert Unix timestamps to local time
                result_data["time"] = result_data["timestamp"].apply(
                    lambda x: utils.convert_unix_to_local(x, client_timezone)
                )

            if not result_data.empty:
                st.line_chart(
                    result_data.set_index("time")[["sent_Mbps", "received_Mbps"]]
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
