import os
import glob
from flask import Flask, request, session, send_file, make_response
from flask_cors import CORS, cross_origin
from model_client import get_prediction
import sys

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['nii', 'nii.gz'])

app = Flask(__name__)

CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/test', methods=['GET'])
def test():
    return 'test works'

@app.route('/upload', methods=['POST'])
def fileUpload():
    target=os.path.join(UPLOAD_FOLDER,'images')
    f = request.files['file']
    filename = f.filename
    destination="/".join([os.path.abspath(os.getcwd()), target, filename])
    f.save(destination)
    #session['uploadFilePath']=destination
    response="OK"
    return response

@app.route('/predict', methods=['GET'])
def prediction():
    target = os.path.join(UPLOAD_FOLDER,'images')
    destination = "/".join([os.path.abspath(os.getcwd()), target, '*'])
    list_of_files = glob.glob(destination)
    latest_file = max(list_of_files,key=os.path.getctime)

    data = request.args
    coords = [int(data.get('x')), int(data.get('y')), int(data.get('z'))]
    showMaps = data.get('showMaps')

    try:
        host_ip = 'crohns'
        print(host_ip, file=sys.stderr)
        prediction = get_prediction(coords,latest_file,host_ip)
        response = send_file('./feature_map_image.nii', attachment_filename='feature_map_image.nii') if showMaps.lower() == 'true' else make_response()
        response.headers['Score'] = prediction
        response.headers['Access-Control-Expose-Headers'] = 'Score'
        print(response.headers)

        return response
    except Exception:
        print("An error occured when extracting the feature maps.")
        return "An error occured when extracting the feature maps."

app.run(host='0.0.0.0', port=9000)
