from .node import Node


"""
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']
"""
if __name__ == "__main__":
    config = {
    'id' : '2',
    'addr':  '18.223.255.142',
    'peers': ['18.119.17.134', '18.117.80.212']
    }

    node2 = Node(config)
    node2.run()
