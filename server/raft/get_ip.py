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

def get_host_ip():
    # get local host ip address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    print(get_host_ip())
