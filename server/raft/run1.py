from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '1',
    'addr': ('18.119.17.134', 10001),
    'peers': { '2':('18.223.255.142', 10002),  '3':('18.117.80.212', 10003)}
    }

    node1 = Node(config)
    node1.run()
