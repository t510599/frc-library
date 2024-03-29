from flask import *
import api
import db
import cv2
from model.CustomEncoder import CustomEncoder
import pickle
import os.path as path
from timeit import default_timer as timer
import flask_login

app = Flask(__name__, static_folder='assets')
manager = flask_login.LoginManager()
manager.session_protection = 'strong'
manager.init_app(app)

#host, user, password
database = db.LibraryDb('', '', '')
app.config.from_object('secret.config')
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = "./upload"
identified_username = None
identify_result = False

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

def gen(camera):
    global identified_username
    global identify_result
    while True:
        frame = camera.get_frame()
        encoding = encodings
        if frame is None:
            camera.refresh()
            del encoding
            continue
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

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        try:
            result = api.identify(frame, encoding)
            if not result is None:
                identified_username = result
                identify_result = True
        except api.NoFaceDetectedError:
            pass
        del encoding


#page provider
@app.route('/')
@app.route('/index')
def index():
    print(encodings.keys())
    with open('templates/index.html', 'r') as f:
        return f.read()

@app.route('/register')
def register():
    with open('templates/register.html', 'r') as f:
        return f.read()

@app.route('/borrow')
@flask_login.login_required
def borrow():
    print('in borrow')
    with open('templates/scan.html', 'r') as f:
        return f.read()

@app.route('/return')
def return_page():
    with open('templates/scan.html', 'r') as f:
        return f.read()

@app.route('/log')
@flask_login.login_required
def log():
    with open('templates/log.html', 'r') as f:
        return f.read()

@app.route('/login')
def login_handler():
    print('show login')
    with open('templates/login.html', 'r') as f:
        return f.read()

#apis
@app.route('/api/book/info', methods=["POST"])
def book_info():
    json = request.get_json()
    book_id = json['id']
    mode = json['mode']
    book = database.query_book(book_id)
    if book != None:
        if book.lent != (mode == 'borrow'):
            return jsonify(book)
        else:
            content = {
                'state': False,
                'error': 'book status not match'
            }
            return jsonify(content)
    else:
        content = {
            "state": False,
            'error': 'cannot find the book'
        }
        return jsonify(content)

@app.route('/api/borrow', methods=["POST"])
def borrow_book():
    json = request.get_json()
    book_ids = json['books']
    results = database.borrow_book(book_ids, flask_login.current_user)
    err_id = []
    for i in range(len(results)):
        result = results[i]
        if not result:
            err_id.append(book_ids[i])
    if err_id:
        content = {
            'state': False,
            'err': err_id
        }
        return jsonify(content)
    else:
        return jsonify({'state': True})

@app.route('/api/return', methods=["POST"])
def return_book():
    json = request.get_json()
    book_ids = json['books']
    results = database.return_book(book_ids)
    err_id = []
    for i in range(len(results)):
        result = results[i]
        if not result:
            err_id.append(book_ids[i])
    if err_id:
        content = {
            'state': False,
            'err': err_id
        }
        return jsonify(content)
    else:
        return jsonify({'state': True})

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
        encoded = encoding.tostring()
        user = database.create_user(name, encoded)
        if not user:
            return jsonify({'state': False, 'error': 'cannot insert new user'})
        encodings[name] = encoding
        with open('encodings.pickle', 'wb') as f:
            pickle.dump(encodings, f)
        return jsonify({'state': True})
    else:
        return jsonify({'state': False, 'error': 'cannot find a face in the picture'})

@app.route('/api/identify')
def identify():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

#should fetch current encodings from database and return it
def fetch_encodings():
    return database.query_user_encodings()

def save_encoding_as_pickle(encoding):
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encoding, f)

@app.route('/get_state')
def get_state():
    global identify_result
    global encodings
    identify_result = False
    start = timer()
    new_fetched = False
    while not identify_result:
        end = timer()
        if end - start > 5 and not new_fetched:
            encodings = fetch_encodings()
            save_encoding_as_pickle(encodings)
            new_fetched = True
        if end - start > 20:
            return jsonify({'state': False,
                            'message':'timeout'})
    return jsonify({'state': True,
                    'username': identified_username,
                    'avatar_path': path.join(app.config['UPLOAD_FOLDER'], identified_username+".png")})

@app.route('/api/user')
def user_log():
    uid = flask_login.current_user.uid
    books = database.get_user_log(uid)
    return jsonify({
        'books': books
    })

@app.route('/api/login', methods=["GET"])
def api_login():
    if not identified_username is None:
        user = database.query_user(identified_username)
        print('login user', flask_login.login_user(user))
        return jsonify({'state': True})
    return jsonify({'state': False})

@app.route('/api/logout')
def logout():
    global identify_result
    global identified_username
    identify_result = False
    identified_username = None
    flask_login.logout_user()
    return jsonify({'status': 'succeed'}), 200

#login manager
@manager.user_loader
def load_user(user_id):
    return database.get_user(user_id)

@manager.unauthorized_handler
def unauthorized_handler():
    response = jsonify()
    response.status_code = 302
    response.headers['location'] = './login'
    response.autocorrect_location_header = False
    return response

if __name__ == '__main__':
    encodings = dict()
    try:
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
    except:
        #file not found
        pass
    app.json_encoder = CustomEncoder
    app.run(host='0.0.0.0', threaded=True)
