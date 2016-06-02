from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

tableau20 = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),    
             (148, 103, 189), (140, 86, 75), (23, 190, 207)]

for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.)  

plt.figure(figsize=(12, 9))  
  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.grid(True)
  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()

all_data = []

for j in range(0, 7):
	B = []
	C = [] 
	with open ('B_5000' + str(j) + '.txt') as f:
	   	for line in f:
	   		B.append(int(line))

	with open ('C_5000' + str(j) + '.txt') as f:
	   	for line in f:
	   		C.append(int(line))

	assert len(B) == len(C)

	data = []

	for i in range(0, len(B)):
		b = B[i]
		c = C[i]

		v = (c - b + pow(2, 64) - 1) % (pow(2, 64) - 1)
		v -= 1
		data.append(v)
		all_data.append(v)

	assert len(data) == len(B)

	weights = np.ones_like(data)/float(len(data))
	binwidth = 1
	plt.hist(data, weights=weights, bins=np.arange(min(data), max(data) + binwidth, binwidth), color=tableau20[j], alpha=0.4)

print 'max: ' + str(sorted(all_data)[-2])

#plt.xlim(0, 75)
plt.xlabel('Number of packets lost', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()