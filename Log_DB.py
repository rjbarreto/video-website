from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import path


#SQL access layer initialization
LG_FILE = "loglist.sqlite"
db_exists = False
if path.exists(LG_FILE):
    db_exists = True
    print("\t database already exists")

lg_engine = create_engine('sqlite:///%s'%(LG_FILE), echo=False) #echo = True shows all SQL calls

lg_Base = declarative_base()

#Declaration of data
class Logs(lg_Base):
    __tablename__ = 'logs'
    log_id = Column(Integer, primary_key=True)
    ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    description = Column(String, nullable=False)

    def __repr__(self):
        return "<Logs(Log_id=%d, ip='%s', endpoint='%s', method='%s', timestamp='%s', description='%s')>" % (self.log_id, self.ip, self.endpoint, self.method, self.timestamp, self.description)
    def to_dictionary(self):
        return {"log_id": self.log_id, "ip": self.ip, "endpoint": self.endpoint, "method":self.method, "timestamp": self.timestamp, "description":self.description}

lg_Base.metadata.create_all(lg_engine) #Create tables for the data models

lg_Session = sessionmaker(bind=lg_engine)
lg_session = scoped_session(lg_Session)

# Create a new log
def newLog( ip, endpoint, method, timestamp, description):
    log = Logs(ip=ip, endpoint=endpoint, method=method, timestamp=timestamp, description=description)
    try:
        lg_session.add(log)
        lg_session.commit()
        lg_session.close()
        return 1
    except:
        return None

# Make dictionary of all the logs
def listLogsDICT():
    ret_list = []
    ll = listLogs()
    for l in ll:
        ld = l.to_dictionary()
        ret_list.append(ld)
    return ret_list


# Query all the logs
def listLogs():
    l = lg_session.query(Logs).all()
    lg_session.close()
    return l


if __name__ == "__main__":
    pass        