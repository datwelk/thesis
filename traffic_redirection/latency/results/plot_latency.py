from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

def plot(f, color, alpha):
	x = []
	y = []
	total = 0

	with open (f) as _f:
	   	for line in _f:
	   		x.append(float(line.split(' ')[0]))
	   		# Latency is recorded in microseconds. See controller.py
	   		# line 87. Divide by 1000 to obtain milliseconds.
	   		latency_ms = float(line.split(' ')[1]) / 1e3
	 		y.append(latency_ms)
	 		
	count = len(y)
	total = sum(np.array(y))

	low = min(y)
	high = max(y)
	avg = total / count
	#std = math.sqrt(1/float(count) * sum((np.array(y) - avg)**2))
	std = np.std(np.array(y))

	print 'low: ' + str(low)
	print 'high: ' + str(high) 
	print 'avg: ' + str(avg)
	print 'std: ' + str(std)

	weights = np.ones_like(y)/float(len(y))
	binwidth = 1
	n, b, p = plt.hist(y, weights=weights,bins=np.arange(min(y), 
		max(y) + binwidth, binwidth), color=color, alpha=alpha)
	print 'Peak bin: ' + str(p[np.argmax(n)])

def show_graph(src):
	plt.figure(figsize=(12, 9))  

	plt.xlabel("Latency in milliseconds", fontsize=16)
	plt.ylabel("Relative frequency", fontsize=16) 

	ax = plt.subplot(111)  
	ax.spines["top"].set_visible(False)  
	ax.spines["right"].set_visible(False)    
	ax.get_xaxis().tick_bottom()  
	ax.get_yaxis().tick_left()
	ax.grid(True)
	ax.set_xlim([0, 50])

	plot(src, "#1F77B4", 1)
	plt.show()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Plot latency')
	parser.add_argument('f', help='Input filename')

	args = parser.parse_args(sys.argv[1:])
	show_graph(args.f)
	
