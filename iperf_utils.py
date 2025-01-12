import iperf3
import pandas as pd


def create_iperf_table(data):
    """
    Create a table from iPerf3 JSON data, focusing on interval statistics.

    Args:
        data (dict): iPerf3 JSON data.

    Returns:
        pd.DataFrame: A DataFrame containing interval statistics.
    """
    # Extract intervals
    intervals = data.get("intervals", [])

    # Prepare a list for DataFrame rows
    rows = []
    for interval in intervals:
        summary = interval.get("sum", {})
        rows.append({
            "Start (s)": round(summary.get("start")),
            "End (s)": round(summary.get("end")),
            "Duration (s)": round(summary.get("seconds")),
            "MB": round(summary.get("bytes") / 1e6),
            "MBits per Second": round(summary.get("bits_per_second") / 1e6),
        })

    # Create DataFrame
    df = pd.DataFrame(rows)
    return df


def run_iperf_test(hostname, port, duration):
    """Run an iPerf3 test and return results."""
    client = iperf3.Client()
    client.server_hostname = hostname
    client.port = port
    client.duration = duration
    result = client.run()
    try:
        if result.error:
            return None
        return {
            "sent_Mbps": result.sent_Mbps,
            "received_Mbps": result.received_Mbps,
        }
    except Exception as e:
        return None


if __name__ == '__main__':
    print(run_iperf_test('avi.kour.me', '5201',duration=10))
