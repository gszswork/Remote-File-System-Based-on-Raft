from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '1',
    'addr': ('localhost', 101),
    'peers': ['18.223.255.142', '18.117.80.212']
    }

    node1 = Node(config)
    node1.run()
