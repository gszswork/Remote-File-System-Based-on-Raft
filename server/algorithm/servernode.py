# coding: utf-8

import os, json, socket, time, random
from .log import Log
# 4 actions after receive an message:
# 1. general_process(data): all role will do this
# 2. leader_process(data)
# 3. candidate_process(data)
# 4. follower_process(data)

# The algorithm is based on message driven model, whenever a Node receive a message (from
# client or other Nodes), it will run in one iteration to handle and transmit this message.

class ServerNode(object):
    def __init__(self, conf):
        self.role = 'follower'
        self.id = conf['id']
        self.addr = conf['addr']
        self.peers = conf['peers']

        # initialize the socket for connection.
        # ss is used to receive
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ss.bind(self.addr)
        self.ss.settimeout(2)

        # cs is used to send ,cs is only used in 'send(self,msg,addr)' function
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.current_term = 0
        self.voted_for = None

        if not os.path.exists(self.id):
            os.mkdir(self.id)

        # initialize current_term, voted_for
        self.load()
        self.log = Log(self.id)

        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {_id: self.log.last_log_index + 1 for _id in self.peers}
        self.match_index = {_id: -1 for _id in self.peers}

        # indicate the leader's id, we can get leader's address by id
        self.leader_id = None
        self.leader_addr = None
        # client request
        self.client_addr = None

        # request vote
        self.vote_ids = {_id: 0 for _id in self.peers}

        # set next leader_election time, based on raft the time is random with a bound.
        self.wait_ms = (10, 20)
        self.next_leader_election_time = time.time() + random.randint(*self.wait_ms)
        self.next_heartbeat_time = 0

    def initialize(self):
        while True:
            try:
                try:
                    data, addr = self.recv()
                except Exception as e:
                    data, addr = None, None
                if data is not None and data['type'] == 'request_leader':
                    if self.role == 'leader':
                        res_data = {'ip': self.addr}
                    else:
                        res_data = {'ip': self.peers[self.leader_id]}
                    self.send(res_data, addr)
                    continue
                data = self.redirect(data, addr)
                self.general_process(data)
                if self.role == 'leader':
                    self.leader_process(data)
                if self.role == 'follower':
                    self.follower_process(data)
                if self.role == 'candidate':
                    self.candidate_process(data)
            except Exception as e:
                print(e)
        self.ss.close()
        self.cs.close()

    def general_process(self, data):
        if self.commit_index > self.last_applied:
            self.last_applied = self.commit_index
        if data is not None and data['type'] != 'client_append_entries' and data['term'] > self.current_term:
            self.current_term = data['term']
            self.role = 'follower'
            self.voted_for = None
            self.save()
        return

    def leader_process(self, data):
        '''1. time over: send heart beat messages to followers'''
        t = time.time()
        if t > self.next_heartbeat_time:
            self.next_heartbeat_time = t + random.randint(0, 5)

            for dst_id in self.peers:
                heartbeat = {'type': 'append_entries',
                             'src_id': self.id,
                             'dst_id': dst_id,
                             'term': self.current_term,
                             'leader_id': self.id,
                             'prev_log_index': self.next_index[dst_id] - 1,
                             'prev_log_term': self.log.get_log_term(self.next_index[dst_id] - 1),
                             'entries': self.log.get_entries(self.next_index[dst_id]),
                             'leader_commit': self.commit_index
                             }

                self.send(heartbeat, self.peers[dst_id])

        '''2. receive client request message(signal)'''
        if data is not None and data['type'] == 'client_append_entries':
            data['term'] = self.current_term
            self.log.append_entries(self.log.last_log_index, [data])

            return

        '''receive append_entries_response from followers'''
        if data is not None and data['type'] == 'append_entries_response' and data['term'] == self.current_term:
            if data['success'] == False:
                self.next_index[data['src_id']] -= 1
            else:
                self.match_index[data['src_id']] = self.next_index[data['src_id']]
                self.next_index[data['src_id']] = self.log.last_log_index + 1
        while True:
            count = 0
            N = self.commit_index + 1

            for _id in self.match_index:
                if self.match_index[_id] >= N:
                    count += 1
                if count >= len(self.peers) // 2:
                    self.commit_index = N
                    if self.client_addr:
                        response = {'result': 'Success'}
                        self.send(response, self.client_addr)
                    break
            else:
                break

    def follower_process(self, data):
        '''
        follower process.
        '''
        election_time = time.time()
        if data is not None:
            if data['type'] == 'append_entries':
                if data['term'] == self.current_term:
                    self.next_leader_election_time = election_time + random.randint(*self.wait_ms)
                self.append_entries(data)
            elif data['type'] == 'request_vote':
                self.request_vote(data)
        # time out: become candidate enroll in election.
        if election_time > self.next_leader_election_time:
            self.next_leader_election_time = election_time + random.randint(*self.wait_ms)
            self.role = 'candidate'
            self.current_term += 1
            self.voted_for = self.id
            self.save()
            self.vote_ids = {_id: 0 for _id in self.peers}
        return

    def candidate_process(self, data):
        '''
        candidate process, request vote, maybe become leader.
        '''
        election_time = time.time()
        for dst_id in self.peers:
            if self.vote_ids[dst_id] == 0:
                request = {
                    'type': 'request_vote',
                    'src_id': self.id,
                    'dst_id': dst_id,
                    'term': self.current_term,
                    'candidate_id': self.id,
                    'last_log_index': self.log.last_log_index,
                    'last_log_term': self.log.last_log_term
                }
                self.send(request, self.peers[dst_id])

        if data is not None and data['term'] == self.current_term:
            # 1. receive votes: enroll in election.
            if data['type'] == 'request_vote_response':
                self.vote_ids[data['src_id']] = data['vote_granted']
                vote_count = sum(list(self.vote_ids.values()))
                if vote_count >= len(self.peers) // 2:
                    self.role = 'leader'
                    self.voted_for = None
                    self.save()
                    self.next_heartbeat_time = 0
                    self.next_index = {_id: self.log.last_log_index + 1 for _id in self.peers}
                    self.match_index = {_id: 0 for _id in self.peers}
                    return
            # 2. receive current leader message: become follower of current leader (Current leader didn't die).
            elif data['type'] == 'append_entries':
                self.next_leader_election_time = election_time + random.randint(*self.wait_ms)
                self.role = 'follower'
                self.voted_for = None
                self.save()
                return
        # time out, next round election.
        if election_time > self.next_leader_election_time:
            self.next_leader_election_time = election_time + random.randint(*self.wait_ms)
            self.role = 'candidate'
            self.current_term += 1
            self.voted_for = self.id
            self.save()
            self.vote_ids = {_id: 0 for _id in self.peers}
            return


    def load(self):
        # load the Node current state on local machine
        file_path = self.id + '/state.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.current_term = data['current_term']
            self.voted_for = data['voted_for']
        else:
            self.save()

    def save(self):
        data = {'current_term': self.current_term,
                'current_role': self.role,
                'voted_for': self.voted_for,
                }
        file_path = self.id + '/state.json'
        with open(file_path, 'w') as f:
            json.dump(data, f)

    def send(self, msg, addr):
        msg = json.dumps(msg).encode('utf-8')
        self.cs.sendto(msg, addr)

    def recv(self):
        # recv self.ss
        # recvfrom(65535) The maximum amount of data that can be received is 65535 bytes.
        msg, addr = self.ss.recvfrom(65535)
        return json.loads(msg), addr

    def redirect(self, data, addr):
        # Servers except leader can't handle the client request but only resend (redirect) to the leader.
        # Or it's just a mis-sending message, redirect to the right receiver.
        if data == None:
            return None
        '''client requset '''
        if data['type'] == 'client_append_entries' and self.role != 'leader':
            if self.leader_id:
                # if current role is not leader but it knows leader's ID:
                #   - send the data to leader.
                self.send(data, self.peers[self.leader_id])
            else:
                # if current role is not leader but it don't know leader's ID:
                #   - return None and do nothing.
                return None
        if data['type'] == 'client_append_entries' and self.role == 'leader':
            # if current role is exactly the leader
            #   - remember the client address then start append_entries in leader()
            self.client_addr = addr
            return data
        '''Node inter-messgae'''
        if data['dst_id'] != self.id:
            # if this message is to another Nonde, resend the message to that Node.
            self.send(data, self.peers[data['dst_id']])
            return None
        else:
            return data
        return data

    def append_entries(self, data):
        ''''
        After leader selection, the server group can process client request.
        (a) When the leader receive an client request, it will add add about this request in it's own Log, then send
            data with 'append_entries' type to followers.
        (b) When followers receive the the 'append_entries' data from leader, it will judge whether it can agree with
            the client request responding to this data. And send the respond to leader
        (c) If the result is it can agree with it, the follower will add this request to it's Log.
        * This function is only used in followers.
        '''
        response = {'type': 'append_entries_response',
                    'dst_id': data['src_id'],
                    'src_id': self.id,
                    'term': self.current_term,
                    'success': False
                    }
        # 1. If the append_entry has smaller term, follower will return data['success'] = False to leader.
        if data['term'] < self.current_term:
            response['success'] = False
            self.send(response, self.peers[data['src_id']])
            return

        self.leader_id = data['leader_id']

        # 2. If the append_entry is an heartbeat from leader, the follower will do nothing in append_entries.
        if data['entries'] is []:
            return

        index_last = data['prev_log_index']
        term_last = data['prev_log_term']
        current_term_last = self.log.get_log_term(index_last)
        # 3. If the follower's term is different with leader's , follower will delete the last log in it's Log file
        #    to keep consensus with leader.
        if current_term_last != term_last:
            response['success'] = False
            self.send(response, self.peers[data['src_id']])
            self.log.delete_entries(index_last)

        # all success and save the log.
        else:
            response['success'] = True
            self.send(response, self.peers[data['src_id']])
            self.log.append_entries(index_last, data['entries'])

            leader_commit = data['leader_commit']
            if leader_commit > self.commit_index:
                commit_index = min(leader_commit, self.log.last_log_index)
                self.commit_index = commit_index
        return

    def request_vote(self, data):
        '''
        In follower_process to handle a message with 'request_vote' type
        '''
        response = {'type': 'request_vote_response',
                    'src_id': self.id,
                    'dst_id': data['src_id'],
                    'term': self.current_term,
                    'vote_granted': False
                    }

        if data['term'] < self.current_term:
            response['vote_granted'] = False
            self.send(response, self.peers[data['src_id']])
            return

        candidate_id = data['candidate_id']
        index_last = data['last_log_index']
        term_last = data['last_log_term']
        if self.voted_for is None or self.voted_for == candidate_id:
            # 1. vote for the candidate
            if index_last >= self.log.last_log_index and term_last >= self.log.last_log_term:
                self.voted_for = data['src_id']
                self.save()
                response['vote_granted'] = True
                self.send(response, self.peers[data['src_id']])
            # 2. dont vote because of term
            else:
                self.voted_for = None
                self.save()
                response['vote_granted'] = False
                self.send(response, self.peers[data['src_id']])
            # 3. already voted for other candidate with same or higher term number
        else:
            response['vote_granted'] = False
            self.send(response, self.peers[data['src_id']])
        return


