from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os
from sqlalchemy.orm import sessionmaker
from database.tabledef import *
from PIL import Image
import requests
from io import BytesIO

engine = create_engine('sqlite:///ap.db', echo=True)

app = Flask(__name__)
# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'
app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

dropzone = Dropzone(app)
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'view_images'


@app.route('/')
def home(status = None):
    if not session.get('logged_in'):
        return render_template('login.html', status = status)
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        status = None
        session['logged_in'] = True
    else:
        status = True
        flash('wrong password!')
    return home(status)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

# @app.route('/')
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']
    # handle image upload from Dropzone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename    
            )
            # append image urls
            photo_url = photos.url(filename)
        
            response = requests.get(photo_url)
            img = Image.open(BytesIO(response.content))
            (w, h) = img.size
            photo_info = {'url': photo_url, 'width': w, 'height': h}

            file_urls.append(photo_info)
            
        session['file_urls'] = file_urls
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('upload_image.html')

@app.route('/view_images')
def view_images():
    
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('upload_image'))
        
    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    print(file_urls)
    session.pop('file_urls', None)
    
    return render_template('view_images.html', file_urls=file_urls)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)