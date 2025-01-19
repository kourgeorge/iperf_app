import os
import time
import threading
import pandas as pd

from server_manager import ServerManager
from utils import run_iperf_test


class ServerMonitor:
    """Handles periodic testing of servers."""

    def __init__(self, server_manager:ServerManager):
        self.server_manager = server_manager  # Reference to ServerManager
        self.stop_signal = threading.Event()  # Signal to stop the periodic testing thread
        self.thread = threading.Thread(target=self._periodic_tester, daemon=True)

    def start(self):
        """Start the periodic tester thread."""
        if not self.thread.is_alive():
            self.stop_signal.clear()
            self.thread.start()

    def stop(self):
        """Stop the periodic tester thread."""
        self.stop_signal.set()
        self.thread.join()

    def _get_last_execution_time(self, results_file):
        """Fetch the last execution timestamp from the results file."""
        if os.path.exists(results_file):
            df = pd.read_csv(results_file)
            if not df.empty:
                return df["timestamp"].iloc[-1]  # Return the last timestamp
        return None  # No tests have been executed yet

    def _run_test(self, server):
        """Run the iPerf test for a single server."""
        hostname = server["hostname"]
        port = int(server["port"])
        duration = int(server["duration"])
        results_file = server["results_file"]

        # Run the iPerf test
        result = run_iperf_test(hostname, port, duration)

        # Process the result
        if "sent_Mbps" in result:
            result_data = {
                "timestamp": result['timestamp'],
                "sent_Mbps": round(result["sent_Mbps"], 2),
                "received_Mbps": round(result["received_Mbps"], 2),
            }
        else:
            result_data = {
                "timestamp": result['timestamp'],
                "sent_Mbps": 0,
                "received_Mbps": 0,
            }

        # Save results to file
        df = pd.DataFrame([result_data])
        if not os.path.exists(results_file):
            df.to_csv(results_file, index=False)
        else:
            df.to_csv(results_file, mode="a", header=False, index=False)

    def _periodic_tester(self):
        """Periodically check the servers and run tests if needed."""
        while not self.stop_signal.is_set():
            servers = self.server_manager.get_servers()

            for _, server in servers.iterrows():
                results_file = server["results_file"]
                last_executed = self._get_last_execution_time(results_file)
                interval = server["interval"] * 60  # Convert minutes to seconds

                if last_executed is None or time.time() - last_executed >= interval:
                    # Run the test in a separate thread
                    threading.Thread(target=self._run_test, args=(server,), daemon=True).start()

            # Sleep for a short interval before checking again
            time.sleep(20)


if __name__ == "__main__":
    server_manager = ServerManager()
    server_tester = ServerMonitor(server_manager)

    # Add servers
    server_manager.add_server("avi.kour.me", 5201, 10, 1)  # Interval: 1 minute
    server_manager.add_server("localhost", 5202, 10, 2)  # Interval: 2 minutes

    # Start testing
    server_tester.start()

    # Stop after 2 minutes
    time.sleep(120)
    server_tester.stop()