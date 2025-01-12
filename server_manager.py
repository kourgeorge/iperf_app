import os
import pandas as pd


class ServerManager:
    """Manages server configurations (adding, removing, saving, and loading)."""

    def __init__(self, file_path="servers.csv"):
        self.file_path = file_path

    def get_servers(self):
        """Load server list from a CSV file."""
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path)
        else:
            return pd.DataFrame(columns=["hostname", "port", "duration", "interval", "results_file"])

    def save_servers(self, server_df):
        """Save server list to a CSV file."""
        server_df.to_csv(self.file_path, index=False)

    def add_server(self, hostname, port, duration, interval):
        """Add a new server configuration."""
        server_df = self.get_servers()

        # Check if the server already exists
        if not ((server_df["hostname"] == hostname) &
                (server_df["port"] == port) &
                (server_df["duration"] == duration) &
                (server_df["interval"] == interval)).any():
            new_entry = pd.DataFrame([{
                "hostname": hostname,
                "port": port,
                "duration": duration,
                "interval": interval,
                "results_file": f"{hostname.replace('.', '_')}.csv"
            }])

            server_df = pd.concat([server_df, new_entry], ignore_index=True)
            self.save_servers(server_df)
            print(f"Added server: {hostname}:{port} with duration {duration}s and interval {interval}m.")
            return True
        else:
            print(f"Server configuration for {hostname}:{port} already exists.")
            return False

    def remove_server(self, hostname, port):
        """Remove a server configuration."""
        server_df = self.get_servers()
        server_df = server_df[~((server_df["hostname"] == hostname) & (server_df["port"] == port))]
        self.save_servers(server_df)
        print(f"Removed server: {hostname}:{port}.")
