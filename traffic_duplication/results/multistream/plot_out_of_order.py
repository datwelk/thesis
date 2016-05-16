from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

# Provide result of 1 of the streams, others should be in same directory
parser = argparse.ArgumentParser(description='Plot out of order packets')
parser.add_argument('f', help='Input filename')

args = parser.parse_args(sys.argv[1:])

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

for j in range(0, 7):
    data = []

    with open (args.f[:-5] + str(j) + '.txt') as f:
        for line in f:
            components = line.split(' ')
            received = int(components[0])
            out_of_order = int(components[2])
            data.append(out_of_order / float(received) * 100)

    weights = np.ones_like(data)/float(len(data))   
    plt.hist(data, bins=200, weights=weights, color=tableau20[j], alpha=0.4)
    
plt.xlabel('Percentage of packets out of order', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()
