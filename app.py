from flask import Flask, render_template, request, Response, session
import threading
from datetime import datetime
import socket
import time
from os import stat as os_stat

app = Flask(__name__)
app.config.from_object(__name__)
lock = threading.Lock()

### checks if a file has changed
def is_changed(filename,since):
	return os_stat(filename).st_mtime > since

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
    i = 0
    req_time=time.time()
    while (i < 20 and not (is_changed('cache.txt', req_time))):
        #print ("waiting %d" % i)
        time.sleep(1)
        i += 1
    lock.acquire()
    try:
        with open('cache.txt','r+') as f:
            f.seek(index*10)
            ret = parse_int(f.read(4))
    finally:
        lock.release()
    return ret

### Render web pages from templates
def main_page(content="home", 
	      template="main.tmpl",
	      url="unset", 
	      value="unset", 
	     ):
	now = datetime.now()
	host = socket.gethostbyname(socket.gethostname())
	content += ".tmpl"
	try:
		page_content = render_template(content)
	except:
		page_content = render_template("404.tmpl")
	return render_template(template, 
						   url = url, 
						   timestamp = now, 
						   host = host, 
						   value = value, 
						   content = page_content
						  )
	
# Request Handling
@app.route("/")
def home():
	return main_page()

@app.route("/pages/<page>")
def get_page(page):
		return main_page(page)
	
@app.route("/code/<int:code>")
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
    

@app.route("/<path:other>")
def not_found(other):
	return main_page("404")

    
