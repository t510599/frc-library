from flask import *
import api
import db
import cv2
from model.CustomEncoder import CustomEncoder
import pickle
import os.path as path
from timeit import default_timer as timer

app = Flask(__name__, static_folder='assets')
#host, user, password
database = db.LibraryDb('localhost', 'root', '')
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
    
def gen(camera, encoding):
    while True:
        frame = camera.get_frame()
        if frame is None:
            camera.refresh()
            continue
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        try:
            result = api.identify(frame, encoding)
            if result:
                identified_username = result
                identify_result = True
        except api.NoFaceDetectedError:
            pass
        frame = cv2.resize(frame, (0, 0), fx=2, fy=2)
        height = frame.shape[0]
        width = frame.shape[1]
        small = min(height, width)
        if height != width:
            if small == height:
                should_cut = (width - small)//2
                frame = frame[:, should_cut:(width-should_cut), :]
            else:
                should_cut = (height - small)//2
                frame = frame[should_cut:height-should_cut, :, :]
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')


#page provider
@app.route('/')
@app.route('/index')
def index():
    with open('templates/index.html', 'r') as f:
        return f.read()

@app.route('/register')
def register():
    with open('templates/register.html', 'r') as f:
        return f.read()

@app.route('/scan')
def scan():
    with open('templates/scan.html', 'r') as f:
        return f.read()

@app.route('/log')
def log():
    with open('templates/log.html', 'r') as f:
        return f.read()
@app.route('/login')
def login():
    with open('templates/login.html', 'r') as f:
        return f.read()

#apis
@app.route('/api/book/info')
def book_info():
    json = request.get_json()
    book_id = json['id']
    book = database.query_book(book_id)
    if book != None:
        return jsonify(book)
    else:
        content = {
            'error': 'cannot find the book'
        }
        return jsonify(content)

@app.route('/api/return')
def return_book():
    json = request.get_json()
    book_ids = json['id']
    result = database.return_book()
    content = {
        'status': result
    }
    return jsonify(content)

@app.route('/api/check', methods=['POST'])
def check_username_exists():
    json = request.get_json()
    username = json['username']
    user = database.query_user(username)
    print(user)
    if not user is None:
        return jsonify({'status': False})
    else:
        return jsonify({'status': True})

@app.route('/api/register', methods=['POST'])
def api_register():
    if not request.files:
        print("nofile")
        return jsonify({'status': 'failed', 'error': 'no_file'}), 400
    if not 'username' in request.form:
        print('no name')
        return jsonify({'status': 'failed', 'error': 'no_name'}), 400
    file = request.files['file']
    name = request.form['username']
    file.save(path.join(app.config['UPLOAD_FOLDER'], name+".png"))
    encoding = None
    try:
        encoding = api.train(file)
    except api.NoFaceDetectedError:
        print('no face detected')
    if not encoding is None:
        encodings[name] = encoding
        with open('encodings.pickle', 'wb') as f:
            pickle.dump(encodings, f)
        encoded = encoding.tostring()
        user = database.create_user(name, encoded)
        if not user:
            return jsonify({'state': False, 'error': 'cannot insert new user'})
        return jsonify({'state': True})
    else:
        return jsonify({'state': False, 'error': 'cannot find a face in the picture'})

@app.route('/api/identify')
def identify():
    return Response(gen(VideoCamera(), encodings), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_state')
def get_state():
    while not identify_result:
        pass
    return jsonify({'status': 'succeed',
                    'username': identified_username,
                    'avatar_path': path.join(app.config['UPLOAD_FOLDER'], identified_username+".png")})

@app.route('/api/logout')
def logout():
    identify_result = False
    identified_username = None
    return jsonify({'status': 'succeed'}), 200

if __name__ == '__main__':
    encodings = dict()
    identified_username = None
    identify_result = False
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
    except:
        #file not found
        pass
    app.json_encoder = CustomEncoder
    app.run(host='0.0.0.0', threaded=True)