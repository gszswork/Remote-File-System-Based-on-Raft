from node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '3',
    # 'addr':  ('18.117.80.212', 103),
    'addr': ('localhost', 30001),
    'peers': {'1': ('localhost', 10001),  '2': ('localhost', 20001)}
    }

    node3 = Node(config)
    node3.run()
