import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from flask_caching import Cache
from werkzeug.utils import secure_filename
import librosa, librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment


UPLOAD_FOLDER = 'D:\Programming\FocusStart\ex1'
ALLOWED_EXTENSIONS = set(['mp3'])

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 24 * 1024 * 1024

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                filename))
            return redirect(url_for('uploaded_file', 
                                filename=filename))
    return render_template('mainpage.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/Converter', methods=['GET', 'POST'])
def converter():

    if request.method == 'POST':
        
        source_file = request.files['audiofile']
        destination_file = "wav/audio.wav"

        sound = AudioSegment.from_mp3(source_file)
        sound.export(destination_file, format="wav")

        signal, sr = librosa.load(destination_file, sr=22050)

        fft = np.fft.fft(signal)

        magnitude = np.abs(fft)
        frequency = np.linspace(0, sr, len(magnitude))

        left_frequency = frequency[:int(len(frequency)/2)]
        left_magnitude = magnitude[:int(len(frequency)/2)]

        plt.plot(left_frequency, left_magnitude)
        plt.xlabel("Frequency")
        plt.ylabel("Magnitude")
        plt.legend(['Discrete Fourier transform'])
        plt.savefig("converted_file.png")

    return send_file("converted_file.png", mimetype='image/gif')


if __name__ == '__main__':
    app.run(debug=True)