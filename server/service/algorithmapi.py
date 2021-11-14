import os
import socket
import json
import requests
# socket used in request_respond
requestSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
requestSocket.settimeout(10)
# socket used in leader_request
leadSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# subsequent socket operations will raise a timeout exception
leadSocket.settimeout(10)

#addr_list = ['115.146.94.191','115.146.93.126','139.180.172.244']

def request_respond(logtime, interface, method, filepath=None):
    #request_respond server给algorithm 发 client request, algorithm执行成功会返回True
    #否则False
    local_addr = get_host_ip()
    addr_list = ['172.31.30.79', '172.31.1.229', '172.31.18.154']
    addr_list.remove(local_addr)
    addr = (get_host_ip(), 10001)
    data = {'type': 'client_append_entries',
            'logtime': logtime,
            'interface': interface,
            'method': method}
    if filepath is not None:
        data['filepath'] = filepath
    '''sendTo algorithm'''
    data = json.dumps(data).encode('utf-8')
    requestSocket.sendto(data, addr)
    '''recvFrom algorithm'''
    try:
        res_data, al_addr = requestSocket.recvfrom(65535)
    except Exception as e:
        return False
    res_data = json.loads(res_data)
    print('recv respond succress, next duplicate the state machine ')
    if res_data['result'] == 'Success':
        # * # * # *  uncomment these lines before deploying. * # * # * #
        '''
            if filepath is not None:
            for each_addr in addr_list:
            res = send_and_get(each_addr, interface, method, filepath)
            else:
            for each_addr in addr_list:
            res = send_and_get(each_addr, interface, method)
            '''
        return True
    else:
        return False

# requset who is leader
def leader_request():
    #返回当前leader的IP地址和端口号,保存在一个list中.eg: ['119.162.11.22',10001]
    addr = (get_host_ip(), 10002)
    data = {'type': 'request_leader'}
    '''sendTo algorithm'''
    data = json.dumps(data).encode('utf-8')
    leadSocket.sendto(data, addr)
    '''recvFrom algorithm'''
    try:
        res_data, al_addr = leadSocket.recvfrom(65535)
    except Exception as e:
        #return {'ip': 'None'}
        return None
    res_data = json.loads(res_data)
    return res_data['ip'][0]


# send_and_get http request to other 2 servers
def send_and_get(address, interface, method, filepath = 'null'):
    target = address + interface
    if method == 'GET':
        sresponse = requests.get(target)
    elif method == 'POST':
        if filepath == 'null':
            sresponse = requests.post(target)
        else:
            #To do
            filepathf = os.path.join(os.getcwd(), filepath)
            files = {'file': open(filepathf, 'rb')}
            sresponse = requests.post(target, files=files)
    elif method == 'PUT':
        sresponse = requests.put(target)
    elif method == 'DELETE':
        sresponse = requests.delete(target)
    else:
        sresponse = 'illegal request method'
    return sresponse.text


def get_host_ip():
    # get local host ip address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


