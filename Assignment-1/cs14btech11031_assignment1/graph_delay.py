import re
import numpy as np
import matplotlib.pyplot as plt

with open("output2.txt") as f:
    data = f.read()

data = data.split('\n')[:-1]

x = map(float, [i for i in range(1, 36)])
y = map(float, [(row.split()[0]) for row in data])

fig = plt.figure()
plt.grid()

ax1 = fig.add_subplot(111)

ax1.set_title("Average delay (millisec) v/s time")
ax1.set_xlabel('Time interval (scale = 1 sec)')
ax1.set_ylabel('Average delay')

ax1.plot(x,y,'bo-',c='r',label='Average delay',linewidth = 2)

leg = ax1.legend(loc='upperright')

plt.show()
