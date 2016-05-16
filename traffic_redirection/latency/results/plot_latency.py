from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import math
import argparse, sys

from scipy.stats import norm

x = []
y = []

parser = argparse.ArgumentParser(description='Plot latency')
parser.add_argument('f', help='Input filename')

args = parser.parse_args(sys.argv[1:])

with open (args.f) as f:
   	for line in f:
   		x.append(float(line.split(' ')[0]))
 		y.append(float(line.split(' ')[1]) / 1e3)

# mu, std = norm.fit(y)

low = min(y)
high = max(y)
print 'low: ' + str(low) + ' high: ' + str(high)

# You typically want your plot to be ~1.33x wider than tall.  
# Common sizes: (10, 7.5) and (12, 9)  
plt.figure(figsize=(12, 9))  
  
# Remove the plot frame lines. They are unnecessary chartjunk.  
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
  
# Ensure that the axis ticks only show up on the bottom and left of the plot.  
# Ticks on the right and top of the plot are generally unnecessary chartjunk.  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.grid(True)

weights = np.ones_like(y)/float(len(y))

plt.xlabel("Latency in milliseconds", fontsize=16)
plt.ylabel("Relative frequency", fontsize=16) 
plt.hist(y, bins=120, weights=weights, color="#3F5D7D")

#plt.plot(x, y)
plt.show()

# binwidth = 1
# #plt.hist(y, bins=range(int(math.floor(min(y))), int(math.ceil(max(y))) + binwidth, binwidth), normed=True, facecolor='blue', rwidth=1)
# plt.hist(y, bins=20, normed=True, facecolor='blue', rwidth=1)
# plt.xlabel('Latency in milliseconds')
# plt.ylabel('Frequency')
# plt.show()

# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# plt.plot(x, p, 'k', linewidth=2)
# title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
# plt.title(title)

# plt.show()

# x = np.array([0.0, 25.0, 50.0, 75.0, 90.0, 100.0])
# y = np.array(sorted(y))

# # print max(y)

# y = mlab.prctile(y, p=x)
# plt.plot((len(x) - 1) * x / 100., y, 'bo-')
# plt.xticks((len(x) - 1) * x / 100., map(str, x))
# plt.xlabel('Percentile')
# plt.ylabel('Latency in milliseconds')
# plt.rc('font', family='serif')
# # plt.yticks(np.arange(0, 250 + 10, 10))
# plt.show()