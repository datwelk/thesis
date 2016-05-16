import argparse
import sys
import httplib
import json
from threading import Thread
import threading
import time
import socket

JSONHeaders = {'Content-type': 'application/json','Accept': 'application/json'}

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
		return ret

def clear(ip, switch):
	# Clears all flows on the switch
	path = '/wm/staticflowpusher/clear/' + switch + '/json'
	conn, body = create_connection(ip, None)
	return request(conn, 'GET', path, body)[0] == 200

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
	return request(conn, 'POST', path, body)[0] == 200

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
	return request(conn, 'POST', path, body)[0] == 200

def request_port_stats(ip, switch):
	path = '/wm/core/switch/' + switch + '/port/json'
	conn, body = create_connection(ip, None)
	status, _, response = request(conn, 'GET', path, body)
	if status != 200:
		return (status, None, None, None, None)

	port_reply = json.loads(response)["port_reply"]
	assert int(port_reply[0]["port"][1]["portNumber"]) == 25
	assert int(port_reply[0]["port"][2]["portNumber"]) == 27

	rx_drop_25 = int(port_reply[0]["port"][1]["receiveDropped"])
	tx_drop_25 = int(port_reply[0]["port"][1]["transmitDropped"])
	rx_drop_27 = int(port_reply[0]["port"][2]["receiveDropped"])
	tx_drop_27 = int(port_reply[0]["port"][2]["transmitDropped"])
	return (status, rx_drop_25, tx_drop_25, rx_drop_27, tx_drop_27)

def record_port_stats(rx_drop_25_diff, tx_drop_25_diff, rx_drop_27_diff, tx_drop_27_diff, f):
	f.write(str(rx_drop_25_diff) + ' ' +
		str(tx_drop_25_diff) + ' ' +
		str(rx_drop_27_diff) + ' ' +
		str(tx_drop_27_diff) + '\n')

def start(ip, switch, ip_src, dl_dst, new_dl_dst, ip_dst, n):
	#f = open('output.txt', 'w')

	# First: clear flows
	if clear(ip, switch) == False:
		return

	for i in range(0, n):
		print 'Iteration: ' + str(i)
		# Install flow that flows traffic from A to B
		if passthrough(ip, switch, ip_src, dl_dst) == False:
			return
		time.sleep(2)
		# Request port stats
		# s, rx_drop_25, tx_drop_25, rx_drop_27, tx_drop_27 = request_port_stats(ip, switch)
		# if s != 200:
		# 	return
		# Send traffic to C, stop it at B
		if redirect(ip, switch, ip_src, dl_dst, new_dl_dst) == False:
			return
		time.sleep(1)
		# Request port stats
		# s, rx_drop_25_after, tx_drop_25_after, rx_drop_27_after, tx_drop_27_after = request_port_stats(ip, switch)
		# if s != 200:
		# 	return
		# record_port_stats(rx_drop_25_after - rx_drop_25,
		# 	tx_drop_25_after - tx_drop_25,
		# 	rx_drop_27_after - rx_drop_27,
		# 	tx_drop_27_after - tx_drop_27, 
		# 	f)
		# Stop traffic at C
		if clear(ip, switch) == False:
			return
		time.sleep(2)

	#f.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Test packet loss when rerouting traffic')
	parser.add_argument('-ip', help='The IP address of the host running the Floodlight instance',default='192.168.200.14')
	parser.add_argument('-switch', help='Switch MAC address',default='87:b8:08:9e:01:e9:95:12')
	parser.add_argument('-s', help='Source IP of traffic to be redirected',default='10.0.0.1')
	parser.add_argument('-d', help='Destination MAC address of traffic to be redirected',default='86:7c:a3:4f:7f:36')
	parser.add_argument('-f', help='New destination MAC address',default='96:5f:91:02:cf:3f')
	parser.add_argument('-o', help='New destination IP address and port.', default='10.0.0.2:50000')
	parser.add_argument('-n', help='Number of data points', type=int, default=10)

	args = parser.parse_args(sys.argv[1:])
	start(args.ip, args.switch, args.s, args.d, args.f, args.o, args.n)

