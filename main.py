import streamlit as st

from iperf_utils import run_iperf_test, create_iperf_table

st.title('iPerf3 Server Performance Monitor')

server_hostname = st.text_input('Server Hostname', 'avi.kour.me')
port = st.number_input('Port', min_value=1, max_value=65535, value=5201)
duration = st.slider('Test Duration (s)', min_value=1, max_value=60, value=10)

if st.button('Run iPerf Test'):
    result = run_iperf_test(server_hostname, port, duration)
    result_js = create_iperf_table(result.json)

    st.text(f"Test completed: {round(result.sent_Mbps)} Mbps sent, {round(result.received_Mbps)} Mbps received")

    st.table(result_js)
