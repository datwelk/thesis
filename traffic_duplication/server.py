import flask
from flask import request, Flask
import subprocess
import os
import signal
from ctypes import *
from cutils import *

app = Flask(__name__)
subprocesses = {}

@app.route('/run/start', methods=['POST'])
def post_stop_run():
	# Obtain port param from request
	body = request.get_json()
	port = body['port']

	p = subprocesses[port]

	# Shut down the process
	p.send_signal(signal.SIGUSR1)
	p.communicate()

	if p.returncode != 0:
		body = {'error' : 'Failed to gracefully shut down generator (' + str(p.returncode) + ').'}
		return flask.jsonify(**body), 500

	# Read counter
	tx = get_packet_counter(port)
	if tx < 0:
		body = {'error' : 'Failed to read packet counter. See debug log for info.'}
		return flask.jsonify(**body), 500

	# Reply with the number of sent packets
	body = {'count' : tx}
	return flask.jsonify(**body)

@app.route('/run/stop', methods=['POST'])
def post_start_run():
	# Obtain port param from request
	body = request.get_json()
	port = body['port']

	rv = create_packet_counter(port)
	if rv != 0:
		body = {'error' : 'Failed to create packet counter (' + str(rv) + ') . See debug log for info.'}
		return flask.jsonify(**body), 500

	# Spawn process
	p = subprocess.Popen(['./generator', '-s', '10', 'udp:10.0.0.2:' + port])
	subprocesses[port] = p

	# Check if failed immediately
	if p.returncode:
		body = {'error' : 'Generator exited immediately with code: ' + p.returncode}
		return flask.jsonify(**body), 500

	body = {'success' : True}
	return flask.jsonify(**body)

if __name__ == '__main__':
	app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
	app.run(host='192.168.200.21',port=8080,debug=True)
