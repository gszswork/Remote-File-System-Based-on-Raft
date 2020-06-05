import requests, os
#r = requests.get('http://api.boyang.website/')

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