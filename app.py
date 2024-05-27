from flask import Flask, request, redirect, url_for, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from rembg import remove
from PIL import Image
from threading import Timer

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_background(input_path, output_path):
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)

def delete_file(path):
    os.remove(path)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            output_filename = f"output_{filename.rsplit('.', 1)[0]}.png"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            remove_background(input_path, output_path)
            Timer(900, delete_file, [input_path]).start()  # Delete the input file after 15 minutes
            Timer(900, delete_file, [output_path]).start()  # Delete the output file after 15 minutes
            return jsonify({'filename': output_filename})
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
