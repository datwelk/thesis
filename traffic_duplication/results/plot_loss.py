from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

parser = argparse.ArgumentParser(description='Plot packet loss')
parser.add_argument('C1', help='Sent packets')
parser.add_argument('B', help='Received packets')

args = parser.parse_args(sys.argv[1:])

sent = []
received = []

with open (args.C1) as f:
   	for line in f:
   		sent.append(int(line))

with open (args.B) as f:
	for line in f:
		components = line.split(' ')
		received.append(int(components[0]))

assert len(received) == len(sent) - 1

loss = []

for i in range(0, len(received)):
	count_lost = max(0, sent[i] - received[i])
	loss.append(count_lost / float(sent[i]) * 100)

print 'low: ' + str(min(loss))
print 'high: ' + str(max(loss))
  
plt.figure(figsize=(12, 9))  
  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
ax.grid(True)
  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()

#ax.set_xlim([0, 2])

weights = np.ones_like(loss)/float(len(loss))

binwidth = 0.05
plt.hist(loss, bins=np.arange(min(loss), max(loss) + binwidth, binwidth), weights=weights, color=(23 / 255., 190 / 255., 207 / 255.))
plt.xlabel('Percentage of packets lost', fontsize=16)
plt.ylabel('Relative frequency', fontsize=16)
plt.show()