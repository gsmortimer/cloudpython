from flask import Flask, render_template, request, Response, session
import threading
from datetime import datetime
import socket

app = Flask(__name__)
app.config.from_object(__name__)
lock = threading.Lock()

### string to int, but int must be 0 - 100 (or limit) ###
### returns -1 on failure ###
def parse_int(input, limit=100):
    try:
        if (len(input) > 5):
            x = -1
        else: x = int (input)
        if (x < 0 or x > limit):
            x = -1
    except:
        x = -1
    return x

### write integer to index in file (thread safe)
def update_data(index,value):
    lock.acquire()
    try:
        with open('cache.txt','r+') as f:
            f.seek(index*10)
            f.write(str(value))
            f.seek(index*10+9)
            f.write("\n")
    finally:
        lock.release()

### write integer from index in file (thread safe)
def read_data(index):
    lock.acquire()
    try:
        with open('cache.txt','r+') as f:
            f.seek(index*10)
            ret = parse_int(f.read(4))
    finally:
        lock.release()
    return ret

### Render web pages from templates
def main_page(url="unset", 
			  value="unset", 
			  content="home.tmpl", 
			  template="main.tmpl"
			 ):
	now = datetime.now()
	host = socket.gethostbyname(socket.gethostname())
	return render_template(template, 
						   url = url, 
						   timestamp = now, 
						   host = host, 
						   value = value, 
						   content = render_templete(content)
						  )
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
        update_data(x,val)
        return Response('Success', status=200, mimetype='text/plain')
    return Response('Error', status=400, mimetype='text/plain')
    

@app.route("/<other>")
def not_fount(other):
	return "Sorry, %s Not found" % other

    
