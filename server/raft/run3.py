from .node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '3',
    'addr':  ('18.117.80.212', 10003),
    'peers': [ '1': ('18.119.17.134', 10001), '2': ('18.223.255.142', 10002)]
    }

    node3 = Node(config)
    node3.run()
