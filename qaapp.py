from flask import Flask, abort, request,  redirect, url_for
from QA_DB import *
from flask import render_template

appqa = Flask(__name__)

################################################# Questions #####################################################

# Return JSON of all the questions of a video
@appqa.route("/API/qa/questions/<int:id>/", methods=['GET'])
def returnQuestionsOfVideoJSON(id):
    return {"questions": listQuestionsDICT(id)}

# Create a new question
@appqa.route("/API/qa/questions/", methods=['POST'])
def createNewQuestion():
    # Get relevant information and store in a dictionary
    j=dict()
    j['video_id']= request.values.get('video_id')
    j['question_time']= request.values.get('question_time')
    j['user_id']= request.values.get('user_id')
    j['user_name']= request.values.get('user_name')
    j['text']= request.values.get('text')
    ret = False
    try:
        #insert new question in qa db
        ret = newQuestion(j["video_id"], j["question_time"], j["user_id"], j["user_name"], j["text"])
    except:
        #the arguments were incorrect
        abort(400)     
    if ret:
        return {"video_id": ret}
    else:
        #if there is an error return ERROR 409    
        abort(409)
        
    
################################################# Answers #####################################################    

# Return JSON of all the answers of a specific question
@appqa.route("/API/qa/answers/<int:id>/", methods=['GET'])
def returnAnswersOfVideoJSON(id):
    return {"answers": listAnswersDICT(id)}

# Create a new answer
@appqa.route("/API/qa/answers/", methods=['POST']) 
def createNewAnswer():
    # Get relevant information and store in a dictionary
    j=dict()
    j['question_id']= request.values.get('question_id')
    j['user_id']= request.values.get('user_id')
    j['user_name']= request.values.get('user_name')
    j['text']= request.values.get('text')
    
    ret = False
    try:
        #insert new answer in qa db
        ret = newAnswer(j["question_id"], j["user_id"], j["user_name"], j["text"])
    except:
        #the arguments were incorrect
        abort(400)   
    if ret:
        return {"question_id": ret}
    else:
        #if there is an error return ERROR 409  
        abort(409)

# Run application  
if __name__ == "__main__":
    appqa.run(host='127.0.0.1', port=8001, debug=True)