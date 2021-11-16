from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '1',
    #'addr': ('18.119.17.134', 101),
    'addr': ('localhost', 10001),
    'peers': {'2': ('localhost', 20001),  '3': ('localhost', 30001)}
    }

    node1 = Node(config)
    node1.run()
