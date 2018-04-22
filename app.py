import pdb

from flask import Flask, render_template, jsonify, request
import video_processing
import visual

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    model = video_processing.process_video(request.files['video'])
    visual.get_voxel_map([0, 10, 10], [[5, 5, 5], [5, 5, 6]])

    return jsonify({
        'resp': 'i have responded',
        'colors': [5] * 8000})

if __name__ == '__main__':
    app.run(debug=True)

