from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math

from scipy.stats import norm

xB = []
xC = []
yB = []
yC = []

with open ('B.txt') as f:
   	for line in f:
   		t = line.split(' ')[0]
   		v = line.split(' ')[1]
   		xB.append(int(t))
   		yB.append(int(v))

with open ('C.txt') as f:
   	for line in f:
   		t = line.split(' ')[0]
   		v = line.split(' ')[1]
   		xC.append(int(t))
   		yC.append(int(v))

#assert len(B) == len(C)

# data = []

# for i in range(0, len(B)):
# 	b = B[i]
# 	c = C[i]

# 	if  b < c:
# 		v = c - b - 1
# 		data.append(v)
# 	elif c < b:
# 		v = ((pow(2, 64) - 1) - c) + b - 1 
# 		data.append(v)

# assert len(data) == len(B)

# print 'low: ' + str(min(data))
# print 'high: ' + str(max(data))

lowC = sorted(yC)[0]
print sorted(yC)[0]
if lowC in yB:
	print xB[yB.index(lowC)]
	print xC[yC.index(lowC)]
	print xC[yC.index(lowC)] - xB[yB.index(lowC)]
	print 'Duplication'

yB = yB[-60:]
xB = xB[-60:] 
xC = xC[0:60]
yC = yC[0:60]
xC = np.array(xC)
xC -= 104000
#yC[:] -= [x - 100000 for x in yC]
  
plt.figure(figsize=(12, 9))  
  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.grid(True)
  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()

ax.get_xaxis().set_ticks([])
#ax.get_yaxis().set_ticks([])

#weights = np.ones_like(data)/float(len(data))

plt.plot(xB, yB, 'o', color=(31 / 255., 119 / 255., 180 / 255.))
plt.plot(xC, yC, 'o', color=(197 / 255., 176 / 255., 213 / 255.))
#plt.hist(data, bins=200, weights=weights, color=(31 / 255., 119 / 255., 180 / 255.))
plt.xlabel('Time', fontsize=16)
plt.ylabel('Sequence number', fontsize=16)
plt.show()