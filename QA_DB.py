from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import path


#SQL access layer initialization
QA_FILE = "qa.sqlite"
db_exists = False
if path.exists(QA_FILE):
    db_exists = True
    print("\t database already exists")

qa_engine = create_engine('sqlite:///%s'%(QA_FILE), echo=False) #echo = True shows all SQL calls

qa_Base = declarative_base()

#Declaration of data
class Questions(qa_Base):
    __tablename__ = 'questions'
    question_id = Column(Integer, primary_key=True)
    video_id= Column(Integer, nullable=False )
    question_time = Column(Float, nullable=False)
    user_id = Column(String, nullable=False) 
    user_name = Column(String, nullable=False)
    text=Column(String, nullable=False)

    def __repr__(self):
        return "<Questions(question_id=%d, video_id=%d, question_time=%f, user_id='%s', user_name='%s', text='%s')>" % (self.question_id, self.video_id, self.question_time, self.user_id, self.user_name, self.text)
    def to_dictionary(self):
        return {"question_id": self.question_id, "video_id": self.video_id, "question_time":self.question_time, "user_id": self.user_id, "user_name": self.user_name, "text":self.text}

class Answers(qa_Base):
    __tablename__ = 'answers'
    answer_id= Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)
    user_id = Column(String, nullable=False) 
    user_name = Column(String, nullable=False)
    text=Column(String, nullable=False)

    def __repr__(self):
        return "<Answers(answer_id=%d, question_id=%d, user_id='%s', user_name='%s', text='%s')>" % (self.answer_id, self.question_id, self.user_id, self.user_name, self.text)
    def to_dictionary(self):
        return {"answer_id": self.answer_id, "question_id": self.question_id, "user_id": self.user_id, "user_name": self.user_name, "text":self.text}
    

qa_Base.metadata.create_all(qa_engine) #Create tables for the data models

qa_Session = sessionmaker(bind=qa_engine)
qa_session = scoped_session(qa_Session)

# Make a new question
def newQuestion( video_id, question_time, user_id, user_name, text):
    qst = Questions(video_id=int(video_id), question_time=float(question_time), user_id=user_id, user_name=user_name, text=text)

    try:
        qa_session.add(qst)
        qa_session.commit()
        qa_session.close()
        return 1
    except:
        return None

# Make a new question
def newAnswer(question_id, user_id, user_name, text):
    # if user already has one answer for that specific question, don't make a new answer
    if getUserAnswerOfQuestion(question_id,user_id):
        return None

    asw = Answers(question_id=int(question_id), user_id=user_id, user_name=user_name, text=text)
    try:
        qa_session.add(asw)
        qa_session.commit()
        return 1
    except:
        return None

# Check if the user already answered the question
def getUserAnswerOfQuestion(question_id, user_id):

    a = qa_session.query(Answers).filter(Answers.user_id==user_id).filter(Answers.question_id==int(question_id)).all()
    qa_session.close()
    return a

# Query all the questions of a specific video
def getQuestionsOfVideo(id):
      q =  qa_session.query(Questions).filter(Questions.video_id==id).all()
      qa_session.close()
      return q

# Make dictionary of all the questions of a video
def listQuestionsDICT(id):
    ret_list = []
    lq = getQuestionsOfVideo(id)
    for q in lq:
        qd = q.to_dictionary()
        ret_list.append(qd)
    return ret_list

# Make dictionary of all the answers of a question 
def listAnswersDICT(id):
    ret_list = []
    la = getAnswersOfQuestion(id)
    
    for a in la:
        ad = a.to_dictionary()
        ret_list.append(ad)

    return ret_list  

# Query all the answers of a question
def getAnswersOfQuestion(id):
      a =  qa_session.query(Answers).filter(Answers.question_id==id).all()
      qa_session.close()
      return a

if __name__ == "__main__":
    pass