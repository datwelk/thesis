from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

data = []

parser = argparse.ArgumentParser(description='Plot out of order packets')
parser.add_argument('f', help='Input filename')

args = parser.parse_args(sys.argv[1:])

with open (args.f) as f:
   	for line in f:
   		items = line.split(' ')
   		out_of_order_count = int(items[2])
   		count = int(items[0])
   		data.append((out_of_order_count / float(count)) * 100)

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
plt.xlabel('Percentage of packets out of order', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()