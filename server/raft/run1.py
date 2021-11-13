from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '1',
    'addr': ('172.31.1.229', 10001),
    'peers': { '2':('172.31.18.154', 20001),  '3':('172.31.30.79', 30001)}
    }

    node1 = Node(config)
    node1.run()
