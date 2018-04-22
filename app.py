import pdb

from flask import Flask, render_template, jsonify, request
import video_processing

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    model = video_processing.process_video(request.files['video'])

    return jsonify({'resp': 'i have responded'})

if __name__ == '__main__':
    app.run(debug=True)

