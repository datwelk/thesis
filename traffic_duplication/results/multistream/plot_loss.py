from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

# Provide result of 1 of the streams, others should be in same directory
parser = argparse.ArgumentParser(description='Plot out of order packets')
parser.add_argument('c', help='Controller output')
parser.add_argument('B', help='Input filename')
parser.add_argument('n', help='No streams',default=7,type=int)

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
#ax.set_xlim([0, 50])

z = 0

for j in range(0, args.n):
    sent = []
    received = []
    loss = []
    
    with open (args.c) as f:
        for line in f:
            components = line.split(' ')
            sent.append(int(components[j]))

    with open (args.B[:-5] + str(j) + '.txt') as f:
        for line in f:
            components = line.split(' ')
            received.append(int(components[0]))

    assert(len(sent) == len(received) + 1)

    for i in range(0, len(received)):
        count_lost = max(0, sent[i] - received[i])
        pc = count_lost / float(sent[i]) * 100
        if pc >= 20:
            z += 1
            print "Loss: " + str(pc) + " Received: " + str(received[i]) + " Sent: " + str(sent[i])
        loss.append(pc)

    weights = np.ones_like(loss)/float(len(loss))   
    #binwidth = 0.2
    plt.hist(loss, weights=weights,bins=200,color=tableau20[j], alpha=0.4)

print "No measurements >= 20 percent loss: " + str(z)
    
plt.xlabel('Percentage of packets lost', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()
