import argparse
import sys
import httplib
import json
from threading import Thread
import threading
import time
import socket

JSONHeaders = {'Content-type': 'application/json','Accept': 'application/json'}
t1 = 0
t2 = 0

event = threading.Event()

def create_connection(server, data):
	conn = httplib.HTTPConnection(server, 8080, timeout=10)
	body = json.dumps(data) if data else ''
	return (conn, body)

def request(conn, action, path, body):
	try:
		conn.request(action, path, body, JSONHeaders)
	except Exception, e:
		print e
		print 'Failed to connect to host'
		return False
	else:
		response = conn.getresponse()
		ret = (response.status, response.reason, response.read())
		print ret
		conn.close()
		return response.status == 200

def listening_thread(host):
	ip = host.split(':')[0]
	port = int(host.split(':')[1])

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((ip, port))

	while True:
		s.recv(1296)
		global t2
		t2 = time.time() * 1e6
		break

	s.close()
	event.set()

def clear(ip, switch):
	# Clears all flows on the switch
	path = '/wm/staticflowpusher/clear/' + switch + '/json'
	conn, body = create_connection(ip, None)
	return request(conn, 'GET', path, body)

def passthrough(ip, switch, ip_src, dl_dst):
	flow = {
		"switch":switch,
		"name":"passthrough",
		"priority":"65534",
		"active":"true",
		"eth_type":"0x0800",
		"ipv4_src":ip_src,
		"eth_dst":dl_dst,
		"actions":"output=26"
	}
	path = '/wm/staticflowpusher/json'
	conn, body = create_connection(ip, flow)
	return request(conn, 'POST', path, body)

def redirect(ip, switch, ip_src, dl_dst, new_dl_dst):
	flow = {
		"switch":switch,
		"name":"redirect",
		"priority":"65535",
		"active":"true",
		"eth_type":"0x0800",
		"ipv4_src":ip_src,
		"eth_dst":dl_dst,
		"actions":"set_field=eth_dst->" + new_dl_dst + ",output=27"
	}
	path = '/wm/staticflowpusher/json'
	conn, body = create_connection(ip, flow)
	global t1
	t1 = time.time() * 1e6
	return request(conn, 'POST', path, body)

def record_result(f, i):
	global t1
	global t2
	result = t2 - t1
	f.write(str(i) + ' ' + str(result) + '\n')

def start(ip, switch, ip_src, dl_dst, new_dl_dst, ip_dst, n):
	f = open('output.txt', 'w')
	for i in range(0, n):
		# First: clear flows
		if clear(ip, switch) == False:
			return
		time.sleep(2)
		# Install flow that flows traffic from A to B
		if passthrough(ip, switch, ip_src, dl_dst) == False:
			return
		time.sleep(2)
		# Measure time it takes for redirected traffic to arrive here
		t = Thread(target=listening_thread, args=(ip_dst,))
		t.start()
		# Redirect traffic
		if redirect(ip, switch, ip_src, dl_dst, new_dl_dst) == False:
			return
		# Wait until first packet has arrived
		event.wait()
		event.clear()
		# Record result
		record_result(f, i + 1)
	f.close()

	if clear(ip, switch) == False:
		return

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Test latency when rerouting traffic')
	parser.add_argument('-ip', help='The IP address of the host running the Floodlight instance',default='192.168.200.14')
	parser.add_argument('-switch', help='Switch MAC address',default='87:b8:08:9e:01:e9:95:12')
	parser.add_argument('-s', help='Source IP of traffic to be redirected',default='10.0.0.1')
	parser.add_argument('-d', help='Destination MAC address of traffic to be redirected',default='86:7c:a3:4f:7f:36')
	parser.add_argument('-f', help='New destination MAC address',default='96:5f:91:02:cf:3f')
	parser.add_argument('-o', help='New destination IP address and port. Should be the host running this program.', default='10.0.0.2:50000')
	parser.add_argument('-n', help='Number of data points', type=int, default=10)

	args = parser.parse_args(sys.argv[1:])
	start(args.ip, args.switch, args.s, args.d, args.f, args.o, args.n)

