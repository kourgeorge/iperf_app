import os
import time
import threading
import pandas as pd
from datetime import datetime
from utils import run_iperf_test


class ServerTester:
    """Handles periodic testing of servers."""

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ServerTester, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return

        self.threads = []
        self.__initialized = True

    def _periodic_iperf_tests(self, server_config, interval):
        """Periodically run iPerf tests and save results, retrying if the server is busy."""
        while True:
            server_hostname = server_config["hostname"]
            port = int(server_config["port"])
            duration = int(server_config["duration"])
            results_file = server_config["results_file"]

            # Run the iPerf test
            result = run_iperf_test(server_hostname, port, duration)

            # Check if the server is busy
            if result and "error" in result and "server is busy" in result["error"].lower():
                # print(f"Server {server_hostname}:{port} is busy. Retrying in {interval} minutes...")
                time.sleep(interval * 60)  # Retry after the same interval
                continue

            # If the result is valid, process it
            if result:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result_data = {
                    "timestamp": timestamp,
                    "sent_Mbps": round(result["sent_Mbps"], 2),
                    "received_Mbps": round(result["received_Mbps"], 2),
                }
                df = pd.DataFrame([result_data])

                # Save results to file
                if not os.path.exists(results_file):
                    df.to_csv(results_file, index=False)
                else:
                    df.to_csv(results_file, mode="a", header=False, index=False)

            # Wait for the next test
            time.sleep(interval * 60)  # Convert interval to seconds

    def start_testing(self, server_config):
        """Start testing a specific server configuration in a separate thread."""
        thread = threading.Thread(
            target=self._periodic_iperf_tests,
            args=(server_config, server_config["interval"]),
            daemon=True
        )
        thread.start()
        self.threads.append(thread)

    def run(self, server_manager):
        """Start testing all servers in the manager."""
        server_df = server_manager.get_servers()
        for _, server in server_df.iterrows():
            server_config = {
                "hostname": server["hostname"],
                "port": server["port"],
                "duration": server["duration"],
                "interval": server["interval"],
                "results_file": server["results_file"],
            }
            self.start_testing(server_config)
