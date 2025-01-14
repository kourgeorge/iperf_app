import os
import time
import threading
import pandas as pd

import utils
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

        self.threads = {}  # Dictionary to hold thread handles and stop signals
        self.__initialized = True

    def _periodic_iperf_tests(self, server_config, stop_signal):
        """Periodically run iPerf tests and save results, retrying if the server is busy."""
        while not stop_signal.is_set():
            server_hostname = server_config["hostname"]
            port = int(server_config["port"])
            duration = int(server_config["duration"])
            results_file = server_config["results_file"]

            # Run the iPerf test
            result = run_iperf_test(server_hostname, port, duration)

            # Check if the server is busy
            if result and "error" in result:
                # Retry after the same interval
                time.sleep(server_config["interval"] * 60)
                continue

            # If the result is valid, process it
            if "sent_Mbps" in result:
                result_data = {
                    "timestamp": result['timestamp'],
                    "sent_Mbps": round(result["sent_Mbps"], 2),
                    "received_Mbps": round(result["received_Mbps"], 2),
                }
                df = pd.DataFrame([result_data])

                # Save results to file
                if not os.path.exists(results_file):
                    df.to_csv(results_file, index=False)
                else:
                    df.to_csv(results_file, mode="a", header=False, index=False)

            # Wait for the next test or stop signal
            stop_signal.wait(server_config["interval"] * 60)

    def start_testing(self, server_config):
        """Start testing a specific server configuration in a separate thread."""
        key = f"{server_config['hostname']}:{server_config['port']}"
        if key in self.threads:
            print(f"Testing already running for {key}.")
            return

        stop_signal = threading.Event()
        thread = threading.Thread(
            target=self._periodic_iperf_tests,
            args=(server_config, stop_signal),
            daemon=True
        )
        thread.start()

        self.threads[key] = {"thread": thread, "stop_signal": stop_signal}

    def stop_testing(self, hostname, port):
        """Stop testing a specific server."""
        key = f"{hostname}:{port}"
        if key in self.threads:
            self.threads[key]["stop_signal"].set()  # Signal the thread to stop
            self.threads[key]["thread"].join()  # Wait for the thread to terminate
            del self.threads[key]

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

    @staticmethod
    def test_server(hostname, port):
        """
        Test if an iPerf3 server is running on the given hostname and port.

        :param hostname: The hostname or IP address of the server.
        :param port: The port to test.
        :return: True if the server is running, False otherwise.
        """
        # Run a quick iPerf3 test with duration 1 second
        ping_result = utils.run_iperf_test(hostname, port, 1)

        if 'error' in ping_result:
            # Server is not reachable or not running iPerf3
            return False, ping_result["error"]

        # Server is reachable and running iPerf3
        return True, None
