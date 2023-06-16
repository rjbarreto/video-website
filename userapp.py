from flask import Flask, abort, request,  redirect, url_for
from User_DB import *
from flask import render_template
from time import sleep

appuser = Flask(__name__)

# Make dictionary of all the users
@appuser.route("/API/users/", methods=['GET'])
def returnsUsersJSON():
    return {"users": listUsersDICT()}

# Make dictionary of a specific user
@appuser.route("/API/users/<string:id>/")
def returnUserByIDDICT(id):
    try:
        u = getUserByIDDICT(id)
        return u
    except:
        abort(404)

# Create a new user
@appuser.route("/API/users/", methods=['POST'])
def _createUser():
    # Get relevant information and store in a dictionary
    j=dict()
    j['id']= request.values.get('username')
    j['name']= request.values.get('name')
    j['admin'] = request.values.get('admin')
    ret = False
    try:
        ret = newUser(j["id"], j["name"],j["admin"])
    except:
        #the arguments were incorrect
        abort(400)
        
    if ret:
        return {"data": ret}
    else:
        #if there is an error return ERROR 409 (user is already in the table)
        abort(409)

# Increment number of questions of an user
@appuser.route("/API/users/<string:id>/questions/", methods=['PUT'])        
def _incrementQuestions(id):
    try:
        return {"id":id, "data": incrementQuestions(id)}
    except:
        abort(404)

# Increment number of answers of an user
@appuser.route("/API/users/<string:id>/answers/", methods=['PUT'])        
def _incrementAnswers(id):
    try:
        return {"id":id, "data": incrementAnswers(id)}
    except:
        abort(404)

# Increment number of video views of an user
@appuser.route("/API/users/<string:id>/views/", methods=['PUT'])        
def _incrementViews(id):
    try:
        return {"id":id, "data": incrementViews(id)}
    except:
        abort(404)

# Increment number of videos submitted by the user
@appuser.route("/API/users/<string:id>/videos/", methods=['PUT'])        
def _incrementVideos(id):
    try:
        return {"id":id, "data": incrementVideos(id)}
    except:
        abort(404)

# HTML that shows information about all the users
@appuser.route("/userslist/")
def userslistfunc():
    return appuser.send_static_file('userlistings.html')    

# Run application
if __name__ == "__main__":
    appuser.run(host='127.0.0.1', port=8002, debug=True)