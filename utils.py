import os
import pandas as pd
from iperf3 import iperf3
import pytz
import datetime
import socket


def run_iperf_test(hostname, port, duration):
    """Run an iPerf3 test and return results."""
    client = iperf3.Client()
    client.server_hostname = hostname
    client.port = port
    client.duration = duration
    try:
        result = client.run()
        del client
        if result.error:
            return {
                "timestamp": datetime.datetime.now().timestamp(),
                "error": result.error
            }
        return {
            "timestamp": result.timesecs,
            "sent_Mbps": result.sent_Mbps,
            "received_Mbps": result.received_Mbps,
        }
    except Exception as e:
        return {"error": str(e)}


def load_results(results_file):
    """Load results from a CSV file."""
    if os.path.exists(results_file):
        return pd.read_csv(results_file)
    else:
        return pd.DataFrame(columns=["timestamp", "sent_Mbps", "received_Mbps"])


def convert_unix_to_local(unix_time, client_timezone='UTC'):
    """
    Convert Unix timestamp to local time.

    :param unix_time: Unix timestamp.
    :param client_timezone: The client's timezone (e.g., 'America/New_York').
    :return: Local time as a formatted string.
    """
    try:
        if not isinstance(client_timezone, str):
            raise ValueError(f"Invalid timezone format: {client_timezone}. It must be a string.")
        local_tz = pytz.timezone(client_timezone)
        local_time = datetime.datetime.fromtimestamp(unix_time, tz=local_tz)
        return local_time.strftime('%d/%m/%y %H:%M')
    except Exception as e:
        return f"Error: {e}"


async def test_server_port(hostname, port, timeout=5):
    """
    Test if a server responds on a specific port.

    :param hostname: The server's hostname or IP address.
    :param port: The port number to test.
    :param timeout: Timeout for the connection attempt in seconds.
    :return: True if the server responds, False otherwise.
    """
    try:
        # Create a socket and attempt to connect to the server
        with socket.create_connection((hostname, port), timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        # Server did not respond or connection was refused
        return False
    except Exception as e:
        return False