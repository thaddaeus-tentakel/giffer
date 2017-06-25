import os
import glob
import threading
from flask import Flask, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

import subprocess

def convert(filename):
    subprocess.call(["ffmpeg", "-i", "files/"+ filename, "-vf", "scale=320:-1:sws_dither=ed,fps=10,palettegen", "-y", "/tmp/palette.png"])
    subprocess.call(["ffmpeg", "-i", "files/"+ filename, "-i", "/tmp/palette.png", "-lavfi", "scale=320:-1:sws_dither=ed,fps=10 [x]; [x][1:v] paletteuse", "-y", "files/" + os.path.splitext(filename)[0] + ".gif"])

UPLOAD_FOLDER = '__files/'
ALLOWED_EXTENSIONS = set(['mp4'])

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/files/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(directory=UPLOAD_FOLDER, filename=filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            th = threading.Thread(target=lambda : convert(filename))
            th.start()
            return redirect(url_for('upload_file',
                                    filename=filename))
    files = glob.glob(os.path.join(UPLOAD_FOLDER, "*"))
    html_files = "<ul class=\"list-group\">{}</ul>".format(
                "\n".join(["<li class=\"list-group-item\"><a href=/files/{filename}>{filename}</a></li>".format(filename=os.path.basename(file_)) for file_ in files]))
    return '''
    <!doctype html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    </head>
    <h1>Turn mp4 to gif</h1> 
    <div class="container">
    <div class="well">
    <h2>Upload File</h2>
        <form method=post enctype=multipart/form-data>
        <input type="file" name="file">
        <div class="text-right">
        <input type=submit value=Upload>
        </div>
        </form>
    </div>
    </div>
    <div class="container">
    <div class="well">
    <h2>Files for Download</h2>
    ''' + html_files + '''</div></div>'''
