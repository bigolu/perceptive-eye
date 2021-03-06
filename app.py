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
    colors = None
    if type(model) != type(None):
        print('type of model does not equal none')
        for pose in model:
            colors = visual.get_voxel_map(pose["campose"], pose["3dpoints"]).tolist()
    else:
        print('type of model is none')

    return jsonify({
        'resp': 'i have responded',
        'colors': colors})

if __name__ == '__main__':
    app.run(debug=True)

