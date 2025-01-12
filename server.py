from server_manager import ServerManager
from server_tester import ServerTester


def get_server_manager():
    """Returns the singleton instance of ServerManager."""
    return ServerManager("servers.csv")


def get_server_tester():
    """Returns the singleton instance of ServerTester."""
    return ServerTester()


server_manager = get_server_manager()
server_tester = get_server_tester()

# Start testing all servers in the manager
server_tester.run(server_manager)