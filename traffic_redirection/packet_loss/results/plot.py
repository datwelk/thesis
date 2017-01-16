from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse,sys

from scipy.stats import norm

parser = argparse.ArgumentParser(description='Plot latency')
parser.add_argument('B', help='Results at B')
parser.add_argument('C', help='Results at C')

args = parser.parse_args(sys.argv[1:])

B = []
C = []

with open (args.B) as f:
   	for line in f:
   		B.append(int(line))

with open (args.C) as f:
   	for line in f:
   		C.append(int(line))

assert len(B) == len(C)

data = []
j = 0

for i in range(0, len(B)):
	b = B[i]
	c = C[i]

	if  b < c:
		v = c - b - 1
		data.append(v)
	elif c < b:
		j += 1
		# print 'jow'
		# v = ((pow(2, 64) - 1) - c) + b - 1 
		# data.append(v)

#assert len(data) == len(B)

print 'c < b: ' + str(j)
print 'low: ' + str(min(data))
print 'high: ' + str(max(data))
  
plt.figure(figsize=(12, 9))  
  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.grid(True)
  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_xlim([0, 60])

weights = np.ones_like(data)/float(len(data))

binwidth = 1
plt.hist(data, weights=weights, bins=np.arange(min(data), max(data) + binwidth, binwidth), color=(31 / 255., 119 / 255., 180 / 255.))
plt.xlabel('Number of packets lost', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()