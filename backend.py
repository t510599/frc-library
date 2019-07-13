from flask import *
import cv2
import api
import pickle
import os.path as path

ft = cv2.freetype.createFreeType2()
ft.loadFontData("./edukai-3.ttf", 0)

app = Flask(__name__, static_folder='assets')
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = "./upload"

class VideoCamera(object):
    def __init__(self):
        # 利用opencv開啟攝影機
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def __del__(self):
        self.video.release()

    def refresh(self):
        self.video.release()
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def get_frame(self):
        _success, image = self.video.read()
        return image

def mark_face(image, name, pos):
    top, right, bottom, left = pos
    # mark face
    cv2.rectangle(image, (left, bottom), (right, top), (255, 0, 0), 2, cv2.LINE_AA)
    # name block
    cv2.rectangle(image, (left, bottom), (right, bottom + 30), (255, 0, 0), -1)

    # put name
    ft.putText(image, name, (left + 5, bottom + 5 + 20), 20, (255, 255, 255), -1, cv2.LINE_AA, True)

    return (name, pos)
    
def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            camera.refresh()
            continue
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        try:
            pos, name = api.identify(frame, encodings)
            mark_face(frame, name, pos)
        except api.NoFaceDetectedError:
            pass
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

#page provider
@app.route('/')
def index():
    with open('templates/index.html', 'r') as f:
        return f.read()

@app.route('/register')
def register():
    with open('templates/register.html', 'r') as f:
        return f.read()

@app.route('/barcode')
def barcode():
    with open('templates/barcode.html', 'r') as f:
        return f.read()

@app.route('/user')
def user():
    with open('templates/user.html', 'r') as f:
        return f.read()


@app.route('/api/train', methods=['PUT'])
def train():
    if not request.files:
        return jsonify({'status': 'failed', 'error': 'no_file'}), 400
    if not 'name' in request.form:
        return jsonify({'status': 'failed', 'error': 'no_name'}), 400
    file = request.files['file']
    name = request.form['name']
    file.save(path.join(app.config['UPLOAD_FOLDER'], name+".png"))
    try:
        encoding = api.train(file)
    except api.NoFaceDetectedError:
        pass
    encodings[name] = encoding
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)
    return jsonify({'status': 'succeed'})

@app.route('/api/identify')
def identify():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    encodings = dict()
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
    except:
        #file not found
        #skip it
        pass
    # make sure singleton
    app.run(host='0.0.0.0', threaded=True)