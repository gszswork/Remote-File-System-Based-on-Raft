from .node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '2',
    'addr':  ('172.31.18.154', 20001),
    'peers': { '1': ('172.31.1.229', 10001), '3': ('172.31.30.79', 30001)}
    }

    node2 = Node(config)
    node2.run()
