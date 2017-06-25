import os
import glob
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

import subprocess

UPLOAD_FOLDER = 'files/'
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
            subprocess.call(["ffmpeg", "-i", "files/"+ filename, "-vf", "scale=320:-1:sws_dither=ed,fps=10,palettegen", "-y", "/tmp/palette.png"])
            subprocess.call(["ffmpeg", "-i", "files/"+ filename, "-i", "/tmp/palette.png", "-lavfi", "scale=320:-1:sws_dither=ed,fps=10 [x]; [x][1:v] paletteuse", "-y", "files/" + os.path.splitext(filename)[0] + ".gif"])
            return redirect(url_for('upload_file',
                                    filename=filename))
    files = glob.glob(os.path.join(UPLOAD_FOLDER, "*"))
    print(files)
    html_files = "<ul>{}</ul>".format(
                "\n".join(["<li><a href=/files/{filename}>{filename}</a></li>".format(filename=os.path.basename(file_)) for file_ in files]))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <h1>Files for Download</h1>
    ''' + html_files
