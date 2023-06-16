from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import path

#SQL access layer initialization
DATABASE_FILE = "ytVideos.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class YTVideo(Base):
    __tablename__ = 'YTVideo'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    questions = Column(Integer, default = 0)

    def __repr__(self):
        return "<YouTubeVideo (id=%d Description=%s, URL=%s, Questions=%d>" % (
                                self.id, self.description, self.url,  self.questions)
    def to_dictionary(self):
        return {"video_id": self.id, "description": self.description, "url": self.url, "questions": self.questions}


Base.metadata.create_all(engine) #Create tables for the data models

yt_Session = sessionmaker(bind=engine)
yt_session = scoped_session(yt_Session)

# Query all the videos
def listVideos():
    v = yt_session.query(YTVideo).all()
    yt_session.close()
    return v

# Make dictionary of all the videos
def listVideosDICT():
    ret_list = []
    lv = listVideos()
    for v in lv:
        vd = v.to_dictionary()
        del(vd["url"])
        ret_list.append(vd)
    return ret_list

# Query specific video with id "id"
def getVideo(id):
    v =  yt_session.query(YTVideo).filter(YTVideo.id==id).first()
    yt_session.close()
    return v

# Make a dictionary of a specific video
def getVideoDICT(id):
    return getVideo(id).to_dictionary()

# Save a new video
def newVideo(description , url):
    vid = YTVideo(description = description, url = url, questions = 0)
    try:
        yt_session.add(vid)
        yt_session.commit()
        yt_session.close()
        return 1
    except:
        return None
        
# Increment the number of questions of the video
def incrementVideoQuestions(id):
    try:
        v = yt_session.query(YTVideo).filter(YTVideo.id==id).update({"questions": (YTVideo.questions + 1)})
        yt_session.commit()
        yt_session.close()
        return v
    except:
        return None

if __name__ == "__main__":
    pass