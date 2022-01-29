from flask import Flask, render_template, request, Response, session
#from flask.ext.session import Session
#from flask_session import Session
import threading
from datetime import datetime
import socket

app = Flask(__name__)
app.config.from_object(__name__)
lock = threading.Lock()

def parse_int(input):
    try:
        if (len(input) > 5):
            x = -1
        else: x = int (input)
        if (x < 0 or x >= 100):
            x = -1
    except:
        x = -1
    return x

def update_data(i,val):
    lock.acquire()
    try:
        with open('cache.txt','r+') as f:
            f.seek(i*10)
            f.write(str(val))
            f.seek(i*10+9)
            f.write("\n")
    finally:
        lock.release()

def read_data(i):
    lock.acquire()
    try:
        with open('cache.txt','r+') as f:
            f.seek(i*10)
            ret = parse_int(f.read(4))
    finally:
        lock.release()
    return ret

def main_page(url="unset", value="unset"):
	now = datetime.now()
	host = socket.gethostbyname(socket.gethostname())
	return render_template('home.html', url = url, timestamp = now, host = host, value = value)

@app.route("/")
def home():
	#return app.send_static_file('test.html')
	return main_page("home")

@app.route("/code/<code>")
def code_get_code(code):
	x = parse_int(code)
	if (x >= 0):
		#value=str(session['arr'][x])
		value=str(read_data(x))
		return main_page(url = request.path, value = value)
	return main_page(url = request.path, value = "failed!")

@app.route("/get/<code>")
def get_code(code):
	x = parse_int(code)
	if (x >= 0):
		value=str(read_data(x))
		return Response(value, status=200, mimetype='text/plain')
	return Response('Error', status=400, mimetype='text/plain')
	
@app.route("/set/<code>", methods=['GET', 'POST'])
def set_code(code):
    req = request.args.get('x')
    val = parse_int(req)
    x = parse_int(code)	
    if (x >= 0):
        #arr[x]=val
        update_data(x,val)
    return main_page(url = request.path, value = "set!")

@app.route("/<other>")
def hello(other):
	return "Sorry, %s Not found" % other

#return redirect(url_for('code',code = temp_var))
    
