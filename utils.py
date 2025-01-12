import os
import pandas as pd
from iperf3 import iperf3


def run_iperf_test(hostname, port, duration):
    """Run an iPerf3 test and return results."""
    client = iperf3.Client()
    client.server_hostname = hostname
    client.port = port
    client.duration = duration
    try:
        result = client.run()
        if result.error:
            return {"error": result.error}
        return {
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
