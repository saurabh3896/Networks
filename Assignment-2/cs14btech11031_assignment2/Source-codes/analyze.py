import re, sys, subprocess, numpy as np, matplotlib.pyplot as plt

# error handling
if len(sys.argv) != 2 :
    print "Usage : python download.py [URL]"
    exit(0)

# lists for output and x-coordinates
output, x = [], [1, 3, 5, 7, 9, 14]

# store the output of python code for downloading
for i in x :
    output.append(subprocess.check_output("python download.py " + sys.argv[1] + " " + str(i), shell = True))

# extract the time out of the result
y = [float(''.join(re.findall(".+\nTime taken : (\d+)(\.)(\d+).+", a)[0])) for a in output]

fig = plt.figure()
plt.grid()
# plot
ax1 = fig.add_subplot(111)

# set graph parameters
ax1.set_title("Download time (seconds) v/s Number of connections (N)")
ax1.set_xlabel('Number of connections (N)')
ax1.set_ylabel('Download time (seconds)')

# point labelling
for xy in zip(x, y) :
    ax1.annotate('(%s, %s)' % xy, xy = xy, textcoords = 'data')

# plot with above set parameters
ax1.plot(x, y, 'bo-', c = 'r', label = 'Download time v/s N', linewidth = 2)
leg = ax1.legend(loc = 'upper right')

# show the graph
plt.show()