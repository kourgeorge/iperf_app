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
        """Add or update a server configuration."""
        server_df = self.get_servers()

        # Check if the server already exists
        existing_server_index = server_df[
            (server_df["hostname"] == hostname) & (server_df["port"] == port)
            ].index

        if not existing_server_index.empty:
            # Update the existing server's configuration
            server_df.loc[existing_server_index, "duration"] = duration
            server_df.loc[existing_server_index, "interval"] = interval
            server_df.loc[existing_server_index, "results_file"] = f"{hostname.replace('.', '_')}_{port}.csv"

        else:
            # Add a new server configuration
            new_entry = pd.DataFrame([{
                "hostname": hostname,
                "port": port,
                "duration": duration,
                "interval": interval,
                "results_file": f"{hostname.replace('.', '_')}_{port}.csv"
            }])
            server_df = pd.concat([server_df, new_entry], ignore_index=True)

        # Save the updated DataFrame back to the file
        self.save_servers(server_df)
        return True

    def remove_server(self, hostname, port):
        """Remove a server configuration and delete its results file."""
        server_df = self.get_servers()

        # Find the server to remove
        server_to_remove = server_df[
            (server_df["hostname"] == hostname) & (server_df["port"] == port)
            ]

        if not server_to_remove.empty:
            # Get the results file path
            results_file = server_to_remove.iloc[0]["results_file"]

            # Remove the server from the DataFrame
            server_df = server_df[
                ~((server_df["hostname"] == hostname) & (server_df["port"] == port))
            ]
            self.save_servers(server_df)

            # Delete the results file if it exists
            if os.path.exists(results_file):
                os.remove(results_file)
