from server_manager import ServerManager
from servers_monitor import ServerMonitor


def get_server_manager():
    """Returns the singleton instance of ServerManager."""
    return ServerManager("servers.csv")


server_manager = get_server_manager()
server_monitor = ServerMonitor(server_manager)

# Start testing all servers in the manager
server_monitor.start()