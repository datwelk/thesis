from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

def plot(f, color, alpha):
	x = []
	y = []

	with open (f) as _f:
	   	for line in _f:
	   		x.append(float(line.split(' ')[0]))
	 		y.append(float(line.split(' ')[1]) / 1e3)

	low = min(y)
	high = max(y)
	print 'low: ' + str(low) + ' high: ' + str(high)

	weights = np.ones_like(y)/float(len(y))
	binwidth = 1.5
	plt.hist(y, weights=weights,bins=np.arange(min(y), max(y) + binwidth, binwidth), color=color, alpha=alpha)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Plot latency')
	parser.add_argument('f', help='Input filename')
	parser.add_argument('--f2', help='Comparison')
	parser.add_argument('--f3', help='Comparison #3')

	args = parser.parse_args(sys.argv[1:])
	plt.figure(figsize=(12, 9))  

	plt.xlabel("Latency in milliseconds", fontsize=16)
	plt.ylabel("Relative frequency", fontsize=16) 

	ax = plt.subplot(111)  
	ax.spines["top"].set_visible(False)  
	ax.spines["right"].set_visible(False)    
	ax.get_xaxis().tick_bottom()  
	ax.get_yaxis().tick_left()
	ax.grid(True)
	ax.set_xlim([0, 250])

	if args.f2 is None:
		plot(args.f, "#1F77B4", 1)
	else:
		plot(args.f, "#1F77B4", 0.4)
		plot(args.f2, "#BCBD22", 0.4)
		#plot(args.f3, "#B10318", 0.4)
	
	plt.show()
