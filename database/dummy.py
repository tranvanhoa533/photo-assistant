import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.tabledef import *
 
engine = create_engine('sqlite:///ap.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
user = User("admin","admin")
session.add(user)
 
user = User("vanhoa","123")
session.add(user)
 
user = User("test","test")
session.add(user)
 
# commit the record the database
session.commit()
 
session.commit()
