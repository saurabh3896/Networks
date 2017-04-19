import math, matplotlib.pyplot as plt, os, time, subprocess, sys, threading, re

def server_gbn(i) :
    p = subprocess.Popen(["python" ,"gbn_server.py", sys.argv[1], str(i)], stdout = subprocess.PIPE)
    out1, err = p.communicate()

def client_gbn() :
    global out2
    p = subprocess.Popen(["python" ,"gbn_client.py"], stdout = subprocess.PIPE)
    for c in iter(lambda: p.stdout.read(1), ''):
        #sys.stdout.write(c)
        break
    out2, err = p.communicate()

x, y = [10, 15, 20, 25, 30, 35, 40, 45, 50], []

os.system("sudo tc qdisc del dev lo root")
os.system("sudo tc qdisc add dev lo root netem delay 0ms")
# here
os.system("sudo tc qdisc change dev lo root netem delay 50ms")
os.system("sudo tc qdisc change dev lo root netem loss 1%")

for i in x :
    print "Go-back-N with window size, N =", str(i)
    filename = sys.argv[1]
    t1 = threading.Thread(target = server_gbn, args = (i, ))
    t2 = threading.Thread(target = client_gbn)
    t1.start()
    time.sleep(2)
    t2.start()
    t2.join()
    t1.join()
    # extract the time out of the result
    y.append(float(''.join(re.findall(".+\nTime taken : (\d+)(\.)(\d+).+", out2)[0])))

fig = plt.figure()
plt.grid()
# plot
ax1 = fig.add_subplot(111)

# set graph parameters
ax1.set_title("Download time (in seconds) v/s N")
ax1.set_xlabel('N (window size)')
ax1.set_ylabel('Download time (in seconds)')

# point labelling
for xy in zip(x, y) :
    ax1.annotate('(%s, %s)' % xy, xy = xy, textcoords = 'data')

# plot with above set parameters
label = 'Download time v/s N in Go-back-N'
ax1.plot(x, y, 'bo-', c = 'r', label = label, linewidth = 2)
leg = ax1.legend(loc = 'upper left')

# show the graph
plt.show()