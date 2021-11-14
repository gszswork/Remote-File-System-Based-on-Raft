# coding: utf-8

import os
import json
import time
import socket
import random
import logging
import requests

from log import Log

# logging这一行设置logging.info也可以输出到控制台
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 4 actions after receive an message:
# 1. all_do(data): 所有的role都要做
# 2. leader_do(data)
# 3. candidate_do(data)
# 4. follower_do(data)



class Node(object):
    def __init__(self, conf):
        self.role = 'follower'
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']

        # persistent state
        self.current_term = 0
        self.voted_for = None

        if not os.path.exists(self.id):
            os.mkdir(self.id)

        # init persistent state
        self.load()
        self.log = Log(self.id)

        # volatile state
        # rule 1, 2
        self.commit_index = 0
        self.last_applied = 0

        # volatile state on leaders
        # rule 1, 2
        self.next_index = {_id: self.log.last_log_index + 1 for _id in self.peers}
        self.match_index = {_id: -1 for _id in self.peers}

        # append entries
        self.leader_id = None

        # request vote
        self.vote_ids = {_id: 0 for _id in self.peers}

        # client request
        self.client_addr = None

        # tick
        self.wait_ms = (10, 20)
        self.next_leader_election_time = time.time() + random.randint(*self.wait_ms)
        self.next_heartbeat_time = 0

        # ss is used to receive
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ss.bind(self.addr)
        self.ss.settimeout(2)

        # cs is used to send ,cs is only used in 'send(self,msg,addr)' function
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #lead_req_addr = (self.addr[0], 10002)
        #self.lead_req_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.lead_req_socket.bind(lead_req_addr)

        #self.lead_res_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def load(self):
        # 记载保存到本地的结果，如果没有（第一次运行服务器）就创建一个
        # load值在init中被调用
        file_path = self.id + '/key.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)

            self.current_term = data['current_term']
            self.voted_for = data['voted_for']

        else:
            self.save()

    def save(self):
        data = {'current_term': self.current_term,
                'voted_for': self.voted_for,
                }

        file_path = self.id + '/key.json'
        with open(file_path, 'w') as f:
            json.dump(data, f)


    def send(self, msg, addr):
        msg = json.dumps(msg).encode('utf-8')
        self.cs.sendto(msg, addr)

    def recv(self):
        # recv self.ss 获取所有发送来的data信息，data格式都是固定的 dictionary的格式
        # recvfrom(65535) 是因为The maximum amount of data that can be received is 65535 bytes.
        msg, addr = self.ss.recvfrom(65535)
        return json.loads(msg), addr

    def redirect(self, data, addr):
        # 重定向，follower接收到来自client的要重定向给leader来处理。
        if data == None:
            return None

        if data['type'] == 'client_append_entries':
            if self.role != 'leader':
                if self.leader_id:
                    logging.info('redirect: client_append_entries to leader')
                    self.send(data, self.peers[self.leader_id])
                return None
            else:
                self.client_addr = addr
                return data

        if data['dst_id'] != self.id:
            logging.info('redirect: to ' + data['dst_id'])
            # logging.info('redirec to leader')
            self.send(data, self.peers[data['dst_id']])
            return None
        else:
            return data

        return data

    def append_entries(self, data):
        '''
        append entries rpc
        only used in follower state
        '''
        ''''
        Leader选举出来后，就可以开始处理客户端请求。Leader收到客户端请求后，将请求内容作为一条log日志添加到自己的log记录中，
        并向其它server发送append_entrie(添加日志)请求。其它server收到append_entries请求后，判断该append请求满足接收条件，
        如果满足条件就将其添加到本地的log中，并给Leader发送添加成功的response。Leader在收到大多数server添加成功的response后，
        就将该条log正式提交。提交后的log日志就意味着已经被raft系统接受，并能应用到状态机中了。
        '''
        response = {'type': 'append_entries_response',
                    'src_id': self.id,
                    'dst_id': data['src_id'],
                    'term': self.current_term,
                    'success': False
                    }

        '''1
            如果不符合接收条件
            '''
        if data['term'] < self.current_term:
            logging.info('          2. smaller term')
            logging.info('          3. success = False: smaller term')
            logging.info('          4. send append_entries_response to leader ' + data['src_id'])
            response['success'] = False
            self.send(response, self.peers[data['src_id']])
            return


        self.leader_id = data['leader_id']

        # heartbeat
        if data['entries'] == []:
            logging.info('          4. heartbeat')
            return

        prev_log_index = data['prev_log_index']
        prev_log_term = data['prev_log_term']

        tmp_prev_log_term = self.log.get_log_term(prev_log_index)

        # append_entries: rule 2, 3
        # append_entries: rule 3
        if tmp_prev_log_term != prev_log_term:
            logging.info('          4. success = False: index not match or term not match')
            logging.info('          5. send append_entries_response to leader ' + data['src_id'])
            logging.info('          6. log delete_entries')
            logging.info('          6. log save')

            response['success'] = False
            self.send(response, self.peers[data['src_id']])
            self.log.delete_entries(prev_log_index)

        # append_entries rule 4
        else:
            logging.info('          4. success = True')
            logging.info('          5. send append_entries_response to leader ' + data['src_id'])
            logging.info('          6. log append_entries')
            logging.info('          7. log save')

            response['success'] = True
            self.send(response, self.peers[data['src_id']])
            self.log.append_entries(prev_log_index, data['entries'])

            # append_entries rule 5
            leader_commit = data['leader_commit']
            if leader_commit > self.commit_index:
                commit_index = min(leader_commit, self.log.last_log_index)
                self.commit_index = commit_index
                logging.info('          8. commit_index = ' + str(commit_index))

        return

    def request_vote(self, data):
        '''
        request vote rpc
        only used in follower state
        '''

        response = {'type': 'request_vote_response',
                    'src_id': self.id,
                    'dst_id': data['src_id'],
                    'term': self.current_term,
                    'vote_granted': False
                    }

        # request vote: rule 1
        if data['term'] < self.current_term:
            logging.info('          2. smaller term')
            logging.info('          3. success = False')
            logging.info('          4. send request_vote_response to candidate ' + data['src_id'])
            response['vote_granted'] = False
            self.send(response, self.peers[data['src_id']])
            return

        logging.info('          2. same term')
        candidate_id = data['candidate_id']
        last_log_index = data['last_log_index']
        last_log_term = data['last_log_term']

        if self.voted_for == None or self.voted_for == candidate_id:
            if last_log_index >= self.log.last_log_index and last_log_term >= self.log.last_log_term:
                self.voted_for = data['src_id']
                self.save()
                response['vote_granted'] = True
                self.send(response, self.peers[data['src_id']])
                logging.info('          3. success = True: candidate log is newer')
                logging.info('          4. send request_vote_response to candidate ' + data['src_id'])
            else:
                self.voted_for = None
                self.save()
                response['vote_granted'] = False
                self.send(response, self.peers[data['src_id']])
                logging.info('          3. success = False: candidate log is older')
                logging.info('          4. send request_vote_response to candidate ' + data['src_id'])
        else:
            response['vote_granted'] = False
            self.send(response, self.peers[data['src_id']])
            logging.info('          3. success = False: has vated for ' + self.voted_for)
            logging.info('          4. send request_vote_response to candidate ' + data['src_id'])

        return

    def all_do(self, data):
        '''
        all servers: rule 1, 2
        '''

        logging.info('-------------------------------all------------------------------------------')


        if self.commit_index > self.last_applied:
            self.last_applied = self.commit_index
            logging.info('all: 1. last_applied = ' + str(self.last_applied))

        if data == None:
            return

        if data['type'] == 'client_append_entries':
            return

        if data['type'] == 'request_leader':
            res_data = {'ip': self.peers[self.leader_id]}
            self.send(res_data, self.client_addr)
        
        if data['term'] > self.current_term:
            logging.info('all: 1. bigger term')
            logging.info('     2. become follower')
            self.role = 'follower'
            self.current_term = data['term']
            self.voted_for = None
            self.save()

        return

    def follower_do(self, data):

        '''
        rules for servers: follower
        '''
        logging.info('-------------------------------follower-------------------------------------')

        t = time.time()
        # follower rules: rule 1
        if data != None:

            if data['type'] == 'append_entries':
                logging.info('follower: 1. recv append_entries from leader ' + data['src_id'])

                if data['term'] == self.current_term:
                    logging.info('          2. same term')
                    logging.info('          3. reset next_leader_election_time')
                    self.next_leader_election_time = t + random.randint(*self.wait_ms)
                self.append_entries(data)

            elif data['type'] == 'request_vote':
                logging.info('follower: 1. recv request_vote from candidate ' + data['src_id'])
                self.request_vote(data)

        # follower rules: rule 2
        if t > self.next_leader_election_time:
            logging.info('follower：1. become candidate')
            self.next_leader_election_time = t + random.randint(*self.wait_ms)
            self.role = 'candidate'
            self.current_term += 1
            self.voted_for = self.id
            self.save()
            self.vote_ids = {_id: 0 for _id in self.peers}

        return

    def candidate_do(self, data):
        '''
        rules for fervers: candidate
        '''
        logging.info('-------------------------------candidate------------------------------------')

        t = time.time()
        # candidate rules: rule 1
        for dst_id in self.peers:
            if self.vote_ids[dst_id] == 0:
                logging.info('candidate: 1. send request_vote to peer ' + dst_id)
                request = {
                    'type': 'request_vote',
                    'src_id': self.id,
                    'dst_id': dst_id,
                    'term': self.current_term,
                    'candidate_id': self.id,
                    'last_log_index': self.log.last_log_index,
                    'last_log_term': self.log.last_log_term
                }
                # logging.info(request)

                self.send(request, self.peers[dst_id])

        # if data != None and data['term'] < self.current_term:
        #     logging.info('candidate: 1. smaller term from ' + data['src_id'])
        #     logging.info('           2. ignore')
            # return

        if data != None and data['term'] == self.current_term:
            # candidate rules: rule 2
            if data['type'] == 'request_vote_response':
                logging.info('candidate: 1. recv request_vote_response from follower ' + data['src_id'])

                self.vote_ids[data['src_id']] = data['vote_granted']
                vote_count = sum(list(self.vote_ids.values()))

                if vote_count >= len(self.peers)//2:
                    logging.info('           2. become leader')
                    self.role = 'leader'
                    self.voted_for = None
                    self.save()
                    self.next_heartbeat_time = 0
                    self.next_index = {_id: self.log.last_log_index + 1 for _id in self.peers}
                    self.match_index = {_id: 0 for _id in self.peers}
                    return

            # candidate rules: rule 3
            elif data['type'] == 'append_entries':
                logging.info('candidate: 1. recv append_entries from leader ' + data['src_id'])
                logging.info('           2. become follower')
                self.next_leader_election_time = t + random.randint(*self.wait_ms)
                self.role = 'follower'
                self.voted_for = None
                self.save()
                return

        # candidate rules: rule 4
        if t > self.next_leader_election_time:
            logging.info('candidate: 1. leader_election timeout')
            logging.info('           2. become candidate')
            self.next_leader_election_time = t + random.randint(*self.wait_ms)
            self.role = 'candidate'
            self.current_term += 1
            self.voted_for = self.id
            self.save()
            self.vote_ids = {_id: 0 for _id in self.peers}
            return

    def leader_do(self, data):
        '''
        rules for fervers: leader
        '''
        logging.info('-------------------------------leader---------------------------------------')

        # leader rules: rule 1, 3
        t = time.time()
        if t > self.next_heartbeat_time:
            self.next_heartbeat_time = t + random.randint(0, 5)

            for dst_id in self.peers:
                logging.info('leader：1. send append_entries to peer ' + dst_id)

                request = {'type': 'append_entries',
                           'src_id': self.id,
                           'dst_id': dst_id,
                           'term': self.current_term,
                           'leader_id': self.id,
                           'prev_log_index': self.next_index[dst_id] - 1,
                           'prev_log_term': self.log.get_log_term(self.next_index[dst_id] - 1),
                           'entries': self.log.get_entries(self.next_index[dst_id]),
                           'leader_commit': self.commit_index
                           }

                self.send(request, self.peers[dst_id])

        # leader rules: rule 2
        if data != None and data['type'] == 'client_append_entries':
            data['term'] = self.current_term
            self.log.append_entries(self.log.last_log_index, [data])

            logging.info('leader：1. recv append_entries from client')
            logging.info('        2. log append_entries')
            logging.info('        3. log save')

            return

        # leader rules: rule 3.1, 3.2
        if data != None and data['term'] == self.current_term:
            if data['type'] == 'append_entries_response':
                logging.info('leader：1. recv append_entries_response from follower ' + data['src_id'])
                if data['success'] == False:
                    self.next_index[data['src_id']] -= 1
                    logging.info('        2. success = False')
                    logging.info('        3. next_index - 1')
                else:
                    self.match_index[data['src_id']] = self.next_index[data['src_id']]
                    self.next_index[data['src_id']] = self.log.last_log_index + 1
                    logging.info('        2. success = True')
                    logging.info('        3. match_index = ' + str(self.match_index[data['src_id']]) +  ' next_index = ' + str(self.next_index[data['src_id']]))

        # leader rules: rule 4
        while True:
            N = self.commit_index + 1

            count = 0
            for _id in self.match_index:
                if self.match_index[_id] >= N:
                    count += 1
                if count >= len(self.peers)//2:
                    self.commit_index = N
                    logging.info('leader：1. commit + 1')
                    '''
                    ##############leader respond to client#############
                    '''
                    # send response to client_request
                    if self.client_addr:
                        response = {'result': 'Success'}
                        self.send(response, self.client_addr)
                    # replicate state machine in interface not HERE!

                    break
            else:
                logging.info('leader：2. commit = ' + str(self.commit_index))
                break


    def run(self):
        while True:
            try:
                try:
                    data, addr = self.recv()
                except Exception as e:
                    # logging.info(e)
                    data, addr = None, None

                data = self.redirect(data, addr)

                self.all_do(data)

                if self.role == 'follower':
                    self.follower_do(data)

                if self.role == 'candidate':
                    self.candidate_do(data)

                if self.role == 'leader':
                    self.leader_do(data)

            except Exception as e:
                logging.info(e)

        self.ss.close()
        self.cs.close()

    def respond_to_lead_req(self):
        while True:
            try:
                try:
                    logging.warn('-------------------------------request------------------------------------------')
                    data, addr = self.lead_req_socket.recvfrom(65535)
                    data = json.loads(data)
                    if data is not None and data['type'] == 'request_leader':
                        if self.role == 'leader':
                            res_data = {'ip': self.addr}
                        else:
                            res_data = {'ip': self.peers[self.leader_id]}
                        res_data = json.dumps(res_data).encode('utf-8')
                        self.lead_res_socket.sendto(res_data, addr)

                except Exception as e0:
                    print(e0)
            except Exception as e1:
                print(e1)
