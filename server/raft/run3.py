from .node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '3',
    'addr':  ('172.31.30.79', 30001),
    'peers': [ '1': ('172.31.1.229', 10001), '2': ('172.31.18.154', 20001)]
    }

    node3 = Node(config)
    node3.run()
