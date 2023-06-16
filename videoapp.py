from flask import Flask, abort, request,  redirect, url_for
from Video_DB import *
from flask import render_template

appvideo = Flask(__name__)

# Returns JSON of a specific video
@appvideo.route("/API/videos/<int:id>/")
def returnSingleVideoJSON(id):  
    try:
        v = getVideoDICT(id)
        return v
    except:
        abort(404)

# Returns JSON of all the videos
@appvideo.route("/API/videos/", methods=['GET'])
def returnsVideosJSON():
    return {"videos": listVideosDICT()}

# Increment the number of questions of a specific video
@appvideo.route("/API/videos/<int:id>/questions/",methods=['PUT'])
def _incrementVideoQuestions(id):
    try:
        return {"id":id, "data": incrementVideoQuestions(id)}
    except:
        abort(404)

# Create a new video
@appvideo.route("/API/videos/", methods=['POST'])
def createNewVideo():
    # Get relevant information and store in a dictionary
    j=dict()
    j['description']= request.values.get('description')
    j['url']= request.values.get('url')
    print(j)

    ret = False
    try:
        ret = newVideo(j["description"], j['url'])
    except:
        #the arguments were incorrect
        abort(400)
        
    if ret:
        return {"id": ret}
    else:
        #if there is an error return ERROR 409
        abort(409)
    
# HTML template that shows the video page of a specific video
@appvideo.route("/showvideo/<int:id>/")
def showvideofunc(id):
    # Send user ID and name to the html
    data=dict()
    data['username']=request.args.get("username")
    data['name']=request.args.get("name")
    return render_template('showvideo.html', videoID=id, username=data['username'], name=data['name'])

# HTML that lists all the videos
@appvideo.route("/videolist/")
def videolistfunc():
    # Send user ID to the html
    data=dict()
    data['username']=request.args.get("username")
    return render_template('videolistings.html', user_id = data['username'])    

# Run application   
if __name__ == "__main__":
    appvideo.run(host='127.0.0.1', port=8000, debug=True)