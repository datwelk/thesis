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

def passthrough(ip_controller, mac_switch, ip_A, mac_B):
	flow = {
		"switch":mac_switch,
		"name":"passthrough",
		"priority":"65534",
		"active":"true",
		"eth_type":"0x0800",
		"ipv4_src":ip_A,
		"eth_dst":mac_B,
		"actions":"output=26"
	}
	path = '/wm/staticflowpusher/json'
	conn, body = create_connection(ip_controller, flow)
	return request(conn, 'POST', path, body)[0] == 200

def duplicate(ip_controller, mac_switch, ip_A, mac_B, mac_C, mac_D):
	flow = {
		"switch":mac_switch,
		"name":"redirect",
		"priority":"65535",
		"active":"true",
		"eth_type":"0x0800",
		"ipv4_src":ip_A,
		"eth_dst":mac_B,
		"actions":"set_field=eth_dst->FF:FF:FF:FF:FF:FF,output=26,output=27,output=28" 
	}
	path = '/wm/staticflowpusher/json'
	conn, body = create_connection(ip_controller, flow)
	return request(conn, 'POST', path, body)[0] == 200

def request_traffic_start(source_port_A):
	conn, body = create_connection('192.168.200.21', {'port' : str(source_port_A)})
	return request(conn, 'POST', '/run/start', body)[0] == 200

def request_traffic_stop(source_port_A):
	conn, body = create_connection('192.168.200.21', {'port' : str(source_port_A)})
	status, _, response = request(conn, 'POST', '/run/stop', body)
	count = json.loads(response)['count']
	return status, count

def start(ip_controller, mac_switch, ip_A, mac_B, mac_C, mac_D, n):
	f = open('output.txt', 'w')

	sockets = [50000, 50001, 50002, 50003, 50004, 50005, 50006]

	# First: clear flows
	if clear(ip_controller, mac_switch) == False:
		return

	for i in range(0, n):
		print 'Iteration: ' + str(i)
		# Connect A and B
		if passthrough(ip_controller, mac_switch, ip_A, mac_B) == False:	
			return
		# if duplicate(ip_controller, mac_switch, ip_A, mac_B, mac_C, mac_D) == False:
		#  	return
		# Start generating traffic
		for s in sockets:
			if request_traffic_start(s) == False:
				return
		# Let traffic flow for 2 secs
		time.sleep(2)
		results = []
		# Stop traffic
		for s in sockets:
			success, count = request_traffic_stop(s)
			results.append(str(count))
			if success == False:
				return
		# Clear flows
		if clear(ip_controller, mac_switch) == False:
			return
		# Let B detect traffic starvation
		time.sleep(2)
		# Write number of transmitted packets from A to file
		f.write(' '.join(results) + '\n')

	f.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Test packet loss when rerouting traffic')
	parser.add_argument('-ip_controller', help='The IP address of the host running the Floodlight instance',default='192.168.200.14')
	parser.add_argument('-mac_switch', help='Switch MAC address',default='87:b8:08:9e:01:e9:95:12')
	parser.add_argument('-ip_A', help='Source IP of traffic to be redirected',default='10.0.0.1')
	parser.add_argument('-mac_B', help='Destination MAC address of traffic to be duplicated',default='86:7c:a3:4f:7f:36')
	parser.add_argument('-mac_C', help='MAC address of C',default='96:5f:91:02:cf:3f')
	parser.add_argument('-mac_D', help='MAC address of D',default='f2:24:1f:61:0a:b1')
	parser.add_argument('-n', help='Number of data points', type=int, default=10)

	args = parser.parse_args(sys.argv[1:])
	start(args.ip_controller, args.mac_switch, args.ip_A, args.mac_B, args.mac_C, args.mac_D, args.n)

