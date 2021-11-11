import os, json, hashlib, couchdb, random, time, pprint, datetime, algorithmapi
from flask import Flask, flash, request, redirect, url_for, send_from_directory, make_response
from werkzeug.utils import secure_filename
from shutil import copyfile

UPLOAD_FOLDER = os.path.join('static', 'uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#server = couchdb.Server('http://admin:passw0rd@13.211.162.245:5984/')
server = couchdb.Server('http://admin:1234@18.119.17.134:5984/')
db = server['da']
# Cannot connect to server, database 'da'

targetpath = os.path.join('static', 'log.txt')
logpath = os.path.join(os.getcwd(), targetpath)
#print(logpath)
def save_log(**args):
    #jpath = os.path.join(os.getcwd(), '/service/static/log.json')
    with open(logpath, 'a', encoding = 'utf-8') as f:
        thestr = json.dumps(args) + '\n'
        f.write(thestr)

@app.route('/log', methods=['GET'])
def get_log():
    if request.method == 'GET':
        if os.path.exists(os.path.join(os.getcwd(), 'static')):
            return send_from_directory(os.path.join(os.getcwd(), 'static'), 'log.txt')
        else:
            code = 404
            result = 'file does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)

@app.route('/logpath', methods=['GET'])
def get_logpath():
    code = 200
    result = logpath
    tresult = {'code': code, 'result': result}
    return json.dumps(tresult)



def if_user_exist(name):
    namelist = []
    for id in db:
        namelist.append(db[id]['name'])
    if name in namelist:
        return True
    else:
        return False



@app.route('/', methods=['GET'])
def hello():
    #thetime = datetime.datetime.now().strftime('%H:%M:%S.%f')
    #save_log(logtime=thetime,interface=request.path,method=request.method)
    code = 200
    result = 'hi there'
    tresult = {'code': code, 'result': result}
    return json.dumps(tresult)

@app.route('/leader', methods=['GET'])
def get_leader():
    code = 200
    result = algorithmapi.leader_request()
    tresult = {'code': code, 'result': result}
    return json.dumps(tresult)



@app.route('/users/<name>/<password>', methods=['GET', 'POST'])
def reg_or_log(name, password):
    md = hashlib.md5()
    md.update(password.encode(encoding='utf-8'))
    password = md.hexdigest()
    if request.method == 'POST':
        if if_user_exist(name):
            code = 304
            result = 'user already exists'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)
        doc = {'_id': name, 'name': name, 'password': password, 'token': '', 'mailbox': []}

        thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
        if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
            code = 503
            result = 'service unavailable'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)

        db.save(doc)
        #oldfilePath = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
        cpath = app.config['UPLOAD_FOLDER'] + '/' + name
        newfilePath = os.path.join(os.getcwd(), cpath)
        isExists=os.path.exists(newfilePath)
        if not isExists:
            os.makedirs(newfilePath)
        code = 200
        result = 'user registered successfully'
        tresult = {'code': code, 'result': result}

        return json.dumps(tresult)
    elif request.method == 'GET':
        if not if_user_exist(name):
            code = 404
            result = 'user does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)
        if password == db[name]['password']:
            tempstr = name + str(random.randint(0,99999))
            md.update(tempstr.encode(encoding='utf-8'))
            token = md.hexdigest()
            tdata = db[name]
            tdata['token'] = token

            thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
            if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
                code = 503
                result = 'service unavailable'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)

            db.save(tdata)
            code = 200
            result = 'user login successfully'
            tresult = {'code': code, 'result': result, 'token': token}

            return json.dumps(tresult)
        else:
            code = 403
            result = 'wrong password'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)


def token_to_name(token):
    for id in db:
        if db[id]['token'] == token:
            return db[id]['name']
    return 'null'


def size_transfer(size):
    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    for i in range(len(units) -1, -1, -1):
        if size >= 2 * (1024 ** i):
            return str(int(size / (1024 ** i))) + ' ' + units[i]      


@app.route('/uploads/<token>', methods=['GET', 'POST'])
def upload_file(token):
    username = token_to_name(token)
    newpath = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)

        tfilepath = os.path.join(newpath, filename)
        tfilepath = os.path.join(os.getcwd(), tfilepath)

        thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
        if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method,filepath=tfilepath) == False:
            code = 503
            result = 'service unavailable'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)


        f.save(os.path.join(newpath, filename))
        code = 200
        result = 'file uploaded successfully'
        tresult = {'code': code, 'result': result}

        return json.dumps(tresult)
    elif request.method == 'GET':
        filePath = os.path.join(os.getcwd(), newpath)
        code = 200
        #result = os.listdir(filePath)
        fileslist = os.listdir(filePath)
        result = []
        for afile in fileslist:
            fpath = os.path.join(newpath, afile)
            tempj = {'name': afile, 'size': size_transfer(os.path.getsize(fpath)), 'mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fpath)))}
            result.append(tempj)
        tresult = {'code': code, 'result': result}

        thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
        #save_log(logtime=thetime,interface=request.path,method=request.method)

        return json.dumps(tresult)

@app.route('/uploads/<filename>/<token>', methods=['GET', 'DELETE'])
def uploaded_file(filename, token):
    username = token_to_name(token)
    newpath = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if request.method == 'GET':
        if os.path.exists(os.path.join(newpath, filename)):
            return send_from_directory(newpath, filename)
        else:
            code = 404
            result = 'file does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)
    elif request.method == 'DELETE':
        if os.path.exists(os.path.join(newpath, filename)):
            os.remove(os.path.join(newpath, filename))
            code = 200
            result = 'file deleted successfully'
            tresult = {'code': code, 'result': result}

            thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
            if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
                code = 503
                result = 'service unavailable'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)

            return json.dumps(tresult)
        else:
            code = 404
            result = 'file does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)
            
@app.route('/uploads/<oldfilename>/<newfilename>/<token>', methods=['PUT'])
def change_filename(oldfilename, newfilename, token):
    username = token_to_name(token)
    newpath = os.path.join(app.config['UPLOAD_FOLDER'], username)
    if request.method == 'PUT':
        if os.path.exists(os.path.join(newpath, oldfilename)):
            os.rename(os.path.join(newpath, oldfilename), os.path.join(newpath, newfilename))
            code = 200
            result = 'file name changed successfully'
            tresult = {'code': code, 'result': result}

            thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
            if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
                code = 503
                result = 'service unavailable'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)


            return json.dumps(tresult)
        else:
            code = 404
            result = 'file does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)



@app.route('/sharedfiles/<token>', methods=['GET'])
def get_shared_files(token):
    username = token_to_name(token)
    if request.method == 'GET':
        mailbox = db[username]['mailbox']
        code = 200
        result = 'shared files obtained successfully'
        tresult = {'code': code, 'result': result, 'files': mailbox}


        return json.dumps(tresult)



@app.route('/sharedfiles/<targetusername>/<filename>/<token>', methods=['GET', 'POST', 'DELETE'])
def share_files(targetusername, filename, token):
    username = token_to_name(token)
    if not if_user_exist(targetusername):
        code = 404
        result = 'target user does not exist'
        tresult = {'code': code, 'result': result}
        return json.dumps(tresult)
    if request.method == 'POST':
        tdata = db[targetusername]
        message = {'from': username, 'filename': filename}
        tdata['mailbox'].append(message)

        thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
        if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
            code = 503
            result = 'service unavailable'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)

        db.save(tdata)
        code = 200
        result = 'file shared successfully'
        tresult = {'code': code, 'result': result}

        return json.dumps(tresult)
    #elif request.method == 'GET':
    else:
        tdata = db[username]
        message = {'from': targetusername, 'filename': filename}
        if message in tdata['mailbox']:
            tdata['mailbox'].remove(message)

            thetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S.%f')
            if algorithmapi.request_respond(logtime=thetime,interface=request.path,method=request.method) == False:
                code = 503
                result = 'service unavailable'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)

            db.save(tdata)
            #save_log(logtime=thetime,interface=request.path,method=request.method)
            if request.method == 'GET':
                #tpstr = app.config['UPLOAD_FOLDER'] + '/' + targetusername
                tpstr = os.path.join(app.config['UPLOAD_FOLDER'], targetusername)
                frompath = os.path.join(tpstr, filename)
                tpstr = os.path.join(app.config['UPLOAD_FOLDER'], username)
                filename += '(from_' + targetusername + ')'
                topath = os.path.join(tpstr, filename)
                copyfile(frompath, topath)
                code = 200
                result = 'file accepted successfully'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)
            if request.method == 'DELETE':
                code = 200
                result = 'file refused successfully'
                tresult = {'code': code, 'result': result}
                return json.dumps(tresult)
        else:
            code = 404
            result = 'file does not exist'
            tresult = {'code': code, 'result': result}
            return json.dumps(tresult)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

