from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '2',
    #'addr':  ('18.223.255.142', 102),
    'addr': ('localhost', 20001),
    'peers': {'1': ('localhost', 10001),  '3': ('localhost', 30001)}
    }

    node2 = Node(config)
    node2.run()
