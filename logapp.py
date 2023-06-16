from flask import Flask, abort, request,  redirect, url_for
from Log_DB import *
from flask import render_template
from time import sleep

applog = Flask(__name__)

# Make dictionary of all the logs
@applog.route("/API/logs/", methods=['GET'])
def returnsLogsJSON():
    return {"logs": listLogsDICT()}

# Create a new log
@applog.route("/API/logs/", methods=['POST'])
def _createLog():
    # Get relevant information and store in a dictionary
    j=dict()
    j['ip']= request.values.get('ip')
    j['endpoint']= request.values.get('endpoint')
    j['method']= request.values.get('method')
    j['timestamp'] = request.values.get('timestamp')
    j['description']= request.values.get('description')

    ret = False
    try:
        ret = newLog(j["ip"], j["endpoint"],j["method"], j['timestamp'], j['description'])
    except:
        #the arguments were incorrect
        abort(400)
        
    if ret:
        return {"data": ret}
    else:
        #if there is an error return ERROR 409
        abort(409)


# HTML that shows information about all logs
@applog.route("/loglist/")
def loglistfunc():
    return applog.send_static_file('loglistings.html')   

# Run application
if __name__ == "__main__":
    applog.run(host='127.0.0.1', port=8003, debug=True)