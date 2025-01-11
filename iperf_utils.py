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


def run_iperf_test(server_hostname='avi.kour.me', port=5201, duration=10):
    client = iperf3.Client()
    client.server_hostname = server_hostname
    client.port = port
    client.duration = duration

    result = client.run()

    if result.error:
        return f"Error: {result.error}"
    else:
        print(f"Test completed: {result.sent_Mbps} Mbps sent, {result.received_Mbps} Mbps received")
        return result


if __name__ == '__main__':
    run_iperf_test()
