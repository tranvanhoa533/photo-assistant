from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, Date
from database.tabledef import User, UserImage
from PIL import Image
import requests
from io import BytesIO
import datetime

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
    if not session.get('user_id'):
        return render_template('login.html', status = status)
    else:
        Session = scoped_session(sessionmaker(bind=engine))
        sess = Session()
        query = sess.query(UserImage).filter(UserImage.userid.in_([session['user_id']]))
        result = query.all()
        file_urls = []
        for userimg in result:
            photo_info = {'url': userimg.imgurl, 'width': userimg.imgw, 'height': userimg.imgh}
            file_urls.append(photo_info)
            session['file_urls'] = file_urls
        sess.close()
        return render_template('view_images.html', file_urls=file_urls)


@app.route('/signin', methods=['GET', 'POST'])
def signin(status = None):
    if request.method == 'GET':
        if not session.get('user_id'):
            return render_template('signin.html', status = status)
        else:
            return redirect(url_for('home'))
    elif request.method == 'POST':
        try:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            confirmedpassword = request.form['confirmpassword']

            if password != confirmedpassword:
                return render_template('signin.html', status = True)

            print(email + '\t' + username + '\t' + password + '\t' + confirmedpassword)
            
            Session = scoped_session(sessionmaker(bind=engine))
            sess = Session()
            user = User(username, password, email)
            sess.add(user)
            sess.commit()
            sess.close()
            return redirect(url_for('home'))
        except Exception as ex :
            print("error in insert operation", ex)
            return "Register error"


@app.route('/view_similar_images', methods=['GET', 'POST'])
def view_similarimages():
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('upload_image'))

    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    print(file_urls)

    return render_template('view_similar_images.html', file_urls=file_urls)

@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = scoped_session(sessionmaker(bind=engine))
    sess = Session()
    query = sess.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    print(POST_USERNAME + '\t' + POST_PASSWORD)
    result = query.first()
    sess.close()
    
    if result:
        status = None
        session['user_name'] = POST_USERNAME
        session['user_id'] = result.userid
    else:
        status = True
        flash('wrong password!')
    return home(status)


@app.route("/logout")
def logout():
    session['user_id'] = None
    session.pop('file_urls', None)
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
        Session = scoped_session(sessionmaker(bind=engine))
        sess = Session()
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

            file_urls.insert(0, photo_info)

            userimg = UserImage(session['user_id'], photo_url, img.size, uploaddate='')
            sess.add(userimg)

        sess.commit()
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

    return render_template('view_images.html', file_urls=file_urls)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)