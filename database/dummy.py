import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabledef import *
 
engine = create_engine('sqlite:///ap.db', echo=True)
 
# create a Session
Session = sessionmaker(bind=engine)
session = Session()
 
user = User("admin","admin")
session.add(user)
 
user = User("vanhoa","123", 'vanhoa@xyz')
session.add(user)
 
user = User("test","test")
session.add(user)
 
# commit the record the database

class_image = ClassImage('cay co', 'cay co')
session.add(class_image)

class_image = ClassImage('do vat', 'do vat')
session.add(class_image)

class_image = ClassImage('con nguoi', 'con nguoi')
session.add(class_image)

session.commit()
