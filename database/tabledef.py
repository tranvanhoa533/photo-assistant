from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///ap.db', echo=True)
Base = declarative_base()
 
########################################################################
class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password, email='test@gmail.com'):
        """"""
        self.username = username
        self.password = password
        self.email = email
 
class UserImage(Base):

    __tablename__ = "userimages"
    id = Column(Integer, primary_key=True)
    userid = Column(String)
    imgurl = Column(String)
    imgw = Column(Integer)
    imgh = Column(Integer)
    imghash = Column(String)
    uploaddate = Column(String)

    def __init__(self, userid, imgurl, imgsize, imghash = '', uploaddate = ''):
        self.userid = userid
        self.imgurl = imgurl
        self.imgw = imgsize[0]
        self.imgh = imgsize[1]
        self.imghash = imghash
        self.uploaddate = uploaddate

# create tables
Base.metadata.create_all(engine)