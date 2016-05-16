from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math

from scipy.stats import norm

B = []
C = []

with open ('B.txt') as f:
   	for line in f:
   		B.append(int(line))

with open ('C.txt') as f:
   	for line in f:
   		C.append(int(line))

assert len(B) == len(C)

data = []

for i in range(0, len(B)):
	b = B[i]
	c = C[i]

	if  b < c:
		v = c - b - 1
		data.append(v)
	elif c < b:
		pass
		# print 'jow'
		# v = ((pow(2, 64) - 1) - c) + b - 1 
		# data.append(v)

#assert len(data) == len(B)

print 'low: ' + str(min(data))
print 'high: ' + str(max(data))
  
plt.figure(figsize=(12, 9))  
  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.grid(True)
  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()

weights = np.ones_like(data)/float(len(data))

plt.hist(data, bins=200, weights=weights, color=(31 / 255., 119 / 255., 180 / 255.))
plt.xlabel('Packets lost', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()