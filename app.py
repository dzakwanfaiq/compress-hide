from flask import Flask, render_template, request, send_from_directory
import os
import subprocess
from stegano import lsb

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Validasi ekstensi file
ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png'},
    'audio': {'mp3'},
    'video': {'mp4'}
}

def allowed_file(filename, media_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(media_type, set())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    media_type = request.form.get('type')
    secret_message = request.form.get('message')

    if not file or file.filename == '':
        return "Tidak ada file yang dipilih."

    filename = file.filename

    if not allowed_file(filename, media_type):
        return f"Tipe file tidak sesuai dengan jenis media yang dipilih ({media_type})."

    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    output_filename = f"compressed_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Kompresi berdasarkan jenis media
    if media_type == 'image':
        subprocess.run(['ffmpeg', '-y', '-i', upload_path, '-vf', 'scale=iw/2:ih/2', output_path])
        if secret_message:
            stego_filename = f"stego_{filename}"
            stego_output = os.path.join(OUTPUT_FOLDER, stego_filename)
            lsb.hide(output_path, secret_message).save(stego_output)
            output_filename = stego_filename
    elif media_type == 'audio':
        subprocess.run(['ffmpeg', '-y', '-i', upload_path, '-b:a', '128k', output_path])
    elif media_type == 'video':
        subprocess.run(['ffmpeg', '-y', '-i', upload_path, '-vcodec', 'libx264', '-crf', '28', output_path])
    else:
        return "Tipe media tidak dikenali."

    return render_template('result.html', filename=output_filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/reveal_stego', methods=['POST'])
def reveal_from_upload():
    file = request.files.get('stego_file')
    if not file:
        return "Tidak ada file yang dipilih."

    filepath = os.path.join(UPLOAD_FOLDER, 'temp_stego.png')
    file.save(filepath)

    try:
        message = lsb.reveal(filepath)
        return render_template('reveal.html', message=message)
    except:
        return render_template('reveal.html', message=None)

if __name__ == '__main__':
    app.run(debug=True)
