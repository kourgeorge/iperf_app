from server_manager import ServerManager
from server_tester import ServerTester


def get_server_manager():
    """Returns the singleton instance of ServerManager."""
    return ServerManager("servers.csv")


server_manager = get_server_manager()
server_tester = ServerTester()

# Start testing all servers in the manager
server_tester.run(server_manager)