from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import path

#SQL access layer initialization
US_FILE = "user.sqlite"
db_exists = False
if path.exists(US_FILE):
    db_exists = True
    print("\t database already exists")

us_engine = create_engine('sqlite:///%s'%(US_FILE), echo=False) #echo = True shows all SQL calls

us_Base = declarative_base()

#Declaration of data
class User(us_Base):
    __tablename__ = 'user'
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    admin = Column(Integer, nullable=False) 
    views= Column(Integer, nullable=False)
    videos= Column(Integer, nullable=False)
    questions= Column(Integer, nullable=False)
    answers= Column(Integer, nullable=False)

    def __repr__(self):
        return "<User(User_id='%s', Name='%s', Admin=%d, Views=%d, Videos=%d, Questions=%d, Answers=%d)>" % (self.user_id, self.name, self.admin, self.views, self.videos,self.questions, self.answers)
    def to_dictionary(self):
        return {"user_id": self.user_id, "name": self.name, "admin": self.admin, "views": self.views, "videos":self.videos, "questions": self.questions, "answers":self.answers}


us_Base.metadata.create_all(us_engine) #Create tables for the data models

us_Session = sessionmaker(bind=us_engine)
us_session = scoped_session(us_Session)

# Create a new user
def newUser( user_id, name, admin):
    usr = User(user_id=user_id, name=name, admin=int(admin), views=0, videos=0, questions=0, answers=0)
    try:
        us_session.add(usr)
        us_session.commit()
        us_session.close()
        return 1
    except:
        return None

# Make dictionary of all the users
def listUsersDICT():
    ret_list = []
    lu = listUsers()
    for u in lu:
        ud = u.to_dictionary()
        del(ud["admin"])
        ret_list.append(ud)
    return ret_list

# Make dictionary of a specific user   
def getUserByIDDICT(id):
    u=getUserByID(id).to_dictionary()    
    return u    

# Query all the users
def listUsers():
    u = us_session.query(User).all()
    us_session.close()
    return u

# Query a specific user     
def getUserByID(_id):
    u =  us_session.query(User).filter(User.user_id==_id).first()
    us_session.close()
    return u

# Increment number of answers of the user
def incrementAnswers(id):
    try:
        u = us_session.query(User).filter(User.user_id==id).update({"answers": (User.answers + 1)})
        us_session.commit()
        us_session.close()
        return u
    except:
        return None

# Increment number of questions of the user
def incrementQuestions(id):
    try:
        u = us_session.query(User).filter(User.user_id==id).update({"questions": (User.questions + 1)})
        us_session.commit()
        us_session.close()
        return u
    except:
        return None
        
# Increment number of video views of the user
def incrementViews(id):
    try:
        u = us_session.query(User).filter(User.user_id==id).update({"views": (User.views + 1)})
        us_session.commit()
        us_session.close()
        return u
    except:
        return None

# Increment number of videos submitted by the user
def incrementVideos(id):   
    try:
        u = us_session.query(User).filter(User.user_id==id).update({"videos": (User.videos + 1)})
        us_session.commit()
        us_session.close()
        return u
    except:
        return None

if __name__ == "__main__":
    pass        