from flask import Flask
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify, url_for
from flask import session
from time import sleep
from datetime import datetime

import requests

#necessary so that our server does not need https
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Store IDs of the administrators
admins=["istxxxxxx"] # insert admin id

# URL do proxy+port
url_proxy="127.0.0.1:5000"

#Go to FENIX -> Pessoal ->  Aplicações Externas   -> Gerir Aplicações
#Go to FENIX -> Personal -> External Applications -> Manage Applications
#Click Criar / Create
#Fill the form with the following inforamrion:
#      Namè - name of your Application
#      Description - description of your Application
#      Site - http://127.0.0.1:5000/    !!!!!!!! copy from the conselo when running the application
#      Redirect URL - http://127.0.0.1:5000/fenix-example/authorized   !!!!!!! the endpoint should be exactly this one
#      Scopes - Information
# Create the new application recold
# Click details do get the Client Id and Client Secret and fille the next constructor
app = Flask(__name__)
app.secret_key = "supersekrit"  # Replace this with your own secret!
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example", __name__,
    # this value should be retrived from the FENIX OAuth page
    client_id="",
    # this value should be retrived from the FENIX OAuth page
    client_secret="",
    # do not change next lines
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)

app.register_blueprint(fenix_blueprint)


@app.route('/')
def home_page():
    # The access token is generated everytime the user authenticates into FENIX
    print(fenix_blueprint.session.authorized)
    print("Access token: "+ str(fenix_blueprint.session.access_token))   

    # verification of the user is  logged in
    if fenix_blueprint.session.authorized == True:
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        data=resp.json()
        if data['username'] in admins:
            data['admin']=1    
        else:
            data['admin']=0
        
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "N/A", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:5000/")
        createNewLog(url_proxy, request.path, "POST", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/users/" +" and added a new user with id " + data["username"] +" and name " + data["name"])
        #adds user to userdB
        a=requests.post("http://127.0.0.1:8002" + "/API/users/", data=data)    

    return render_template("appPage.html", loggedIn = fenix_blueprint.session.authorized)

# Endpoint to logout the user
@app.route('/logout')
def logout():
    if fenix_blueprint.session.authorized == True:
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "N/A", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:5000/logout")

    # this clears all server information about the access token of this connection
    res = str(session.items())
    session.clear()
    # when the browser is redirected to home page it is not logged in anymore
    return redirect(url_for("home_page"))

# Endpoint for an authenticated user to access a menu to choose where to go
@app.route('/private/')
def private_page():
    #this page can only be accessed by a authenticated user
    # verification of the user is  logged in
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data = resp.json() 
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "N/A", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:5000" + "/private/")
        return render_template("privPage.html", username=data['username'], name=data['name'])

# Endpoint to access the list of the videos
@app.route('/videolist/')
def _listvideos():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        #send username to next page
        data={'username':data['username']}
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/videolist/")
        a=requests.get("http://127.0.0.1:8000" + "/videolist/", params=data)
        return a.text

# Endpoint to access the html with a page for the video with id "id"
@app.route("/showvideo/<int:id>/")
def _videolistfunc(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        #send username and name to next page
        data={'username':data['username'], 'name':data['name']}
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/showvideo/" +str(id)+"/")
        a=requests.get("http://127.0.0.1:8000" + "/showvideo/"+str(id)+"/", params=data)
        return a.text

# Endpoint to access the information of all the users
@app.route("/userslist/")
def listusers():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        #checks if user is admin
        if data['username'] in admins:
            now = datetime.now().strftime("%H:%M:%S")
            createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/userslist/")
            a=requests.get("http://127.0.0.1:8002" + "/userslist/")
            return a.text
        else:
            return redirect("http://127.0.0.1:5000/private/")


# Endpoint to access the log list
@app.route('/loglist/')
def loglist():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        if data['username'] in admins:
            now = datetime.now().strftime("%H:%M:%S")
            createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8003" + "/loglist/")
            a=requests.get("http://127.0.0.1:8003" + "/loglist/")
            return a.text
        else:
            return redirect("http://127.0.0.1:5000/private/")

#################################### VIDEOS ##################################

# Endpoint to redirect to the videoapp port to return the JSON of all the videos
@app.route('/API/videos/')
def api_videos():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/API/videos/")
        a=requests.get("http://127.0.0.1:8000" + "/API/videos/")
        return a.text

# Endpoint to redirect to the videoapp port with the index of the video
@app.route("/API/videos/<int:id>/")
def api_videos_index(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/API/videos/"+str(id)+"/")
        a=requests.get("http://127.0.0.1:8000" + "/API/videos/"+str(id)+"/")
        return a.text

# Endpoint to redirect to the videoapp port to create a video
@app.route("/API/videos/", methods=['POST'])
def create_video():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        sleep(0.1)
        #send variable j (info abour new video) to next page
        j = request.get_json()
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "POST", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/API/videos/" +" and added a new video with url " +j["url"] +" and description " + j["description"])
        a=requests.post("http://127.0.0.1:8000" + "/API/videos/", data=j)
        return a.text

# Endpoint to redirect to the videoapp port to increment the number of questions of a video
@app.route("/API/videos/<int:id>/questions/", methods=['PUT'])        
def _incrementVideoQuestions(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "PUT", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/API/videos/"+str(id)+"/questions/")
        a=requests.put("http://127.0.0.1:8000" + "/API/videos/"+ str(id) + "/questions/")
        return a.text  

#################################### USERS ##############################

# Endpoint to get information of all users to fill the user table
@app.route("/API/users/")
def return_User():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/users/")
        a=requests.get("http://127.0.0.1:8002" + "/API/users/")
        return a.text

# Endpoint to get information of a specific user
@app.route("/API/users/<string:id>/")
def return_User_index(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/users/"+id+"/")
        a=requests.get("http://127.0.0.1:8002" + "/API/users/"+id+"/")
        return a.text

# Endepoint to increment number of questions of an user 
@app.route("/API/users/<string:id>/questions/", methods=['PUT'])        
def _incrementQuestions(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "PUT", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/users/"+id+"/questions/")
        a=requests.put("http://127.0.0.1:8002" + "/API/users/" + id + "/questions/")
        return a.text 

# Endepoint to increment number of answers of an user 
@app.route("/API/users/<string:id>/answers/", methods=['PUT'])        
def _incrementAnswers(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "PUT", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/users/"+id+"/answers/")
        a=requests.put("http://127.0.0.1:8002" +  "/API/users/"+ id + "/answers/")
        return a.text 

# Endpoint to increment number of videos views by the user
@app.route("/API/users/<string:id>/views/", methods=['PUT'])        
def _incrementViews(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "PUT", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8000" + "/API/users/"+id+"/views/")
        a=requests.put("http://127.0.0.1:8002" +  "/API/users/" + id + "/views/")
        return a.text 

# Endpoint to increment number of videos submitted by the user
@app.route("/API/users/<string:id>/videos/", methods=['PUT'])        
def _incrementVideos(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "PUT", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8002" + "/API/videos/"+id+"/videos/")
        a=requests.put("http://127.0.0.1:8002" + "/API/users/"+ id + "/videos/")
        return a.text    

#################################### Q & A ##############################

#Endpoint to create a new question
@app.route("/API/qa/questions/", methods=['POST'])
def _create_question():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        sleep(0.1)
        j = request.get_json()
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "POST", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8001" + "/API/qa/questions/" +" and added a new question with video id " +str(j["video_id"]) +" , time " + str(j["question_time"]) + " and text " + j["text"])
        a=requests.post("http://127.0.0.1:8001" + "/API/qa/questions/", data=j)
        return a.text

#Endpoint to create a new answer
@app.route("/API/qa/answers/", methods=['POST'])
def _create_answer():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        sleep(0.1)
        j = request.get_json()
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "POST", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8001" + "/API/qa/answers/" +" and added a new answer with question id " +str(j["question_id"]) +" and text " + j["text"])
        a=requests.post("http://127.0.0.1:8001" + "/API/qa/answers/", data=j)
        return a.text

# Enpoint to get all the questions of a specific video
@app.route("/API/qa/questions/<int:id>/")
def _returnQuestionsOfVideoJSON(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8001" + "/API/qa/questions/"+str(id)+"/")
        a=requests.get("http://127.0.0.1:8001" + "/API/qa/questions/"+str(id)+"/")
        return a.text

# Enpoint to get all the answers to a specific question
@app.route("/API/qa/answers/<int:id>/")
def _returnAnswersOfQuestionJSON(id):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8001" + "/API/qa/answers/"+str(id)+"/")
        a=requests.get("http://127.0.0.1:8001" + "/API/qa/answers/"+str(id)+"/")
        return a.text 

#################################### LOG LIST ##############################

# Endpoint to get the information about all logs
@app.route("/API/logs/", methods=['GET'])
def getLogs():
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #if the user is authenticated then a request to FENIX is made
        resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
        #resp contains the response made to /api/fenix/vi/person (information about current user)
        data=resp.json()
        now = datetime.now().strftime("%H:%M:%S")
        createNewLog(url_proxy, request.path, "GET", now, "User " +data["username"]+" connected to: "+"http://127.0.0.1:8003" + "/API/logs/")
        a=requests.get("http://127.0.0.1:8003" + "/API/logs/")
        return a.text 

# Endpoint to create a new log
@app.route("/API/logs/", methods=['POST'])
def createNewLog(ip, endpoint, method, timestamp, description):
    if fenix_blueprint.session.authorized == False:
        #if not logged in browser is redirected to login page (in this case FENIX handled the login)
        return redirect(url_for("fenix-example.login"))
    else:
        #send variable j (info abour new log) to next page
        j=dict()
        j['ip']= ip
        j['endpoint']= endpoint
        j['method']= method
        j['timestamp'] = timestamp
        j['description']= description
        a=requests.post("http://127.0.0.1:8003" + "/API/logs/", data=j)
        return a.text


# Run application
if __name__ == '__main__':
    app.run(debug=True)
