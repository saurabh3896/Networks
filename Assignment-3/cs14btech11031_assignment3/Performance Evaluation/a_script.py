import math, matplotlib.pyplot as plt, os, time, subprocess, sys, threading, re
from matplotlib.ticker import FormatStrFormatter

def server() :
    p = subprocess.Popen(["python" ,"sw_server.py", sys.argv[2]], stdout = subprocess.PIPE)
    out1, err = p.communicate()

def client() :
    global out1
    p = subprocess.Popen(["python" ,"sw_client.py"], stdout = subprocess.PIPE)
    for c in iter(lambda: p.stdout.read(1), ''):
        #sys.stdout.write(c)
        break
    out1, err = p.communicate()

def server_gbn() :
    p = subprocess.Popen(["python" ,"gbn_server.py", sys.argv[2], N], stdout = subprocess.PIPE)
    out1, err = p.communicate()

def client_gbn() :
    global out2
    p = subprocess.Popen(["python" ,"gbn_client.py"], stdout = subprocess.PIPE)
    for c in iter(lambda: p.stdout.read(1), ''):
        #sys.stdout.write(c)
        break
    out2, err = p.communicate()

x, y = [0.0001, 0.001, 0.01, 0.1, 1, 10], []

os.system("sudo tc qdisc del dev lo root")
os.system("sudo tc qdisc add dev lo root netem corrupt 0.0%")

for i in x :
    command = "sudo tc qdisc change dev lo root netem corrupt " + str(i) + "%"
    os.system(command)

    if sys.argv[1] == "1" :
        print "Stop-and-Wait with packet error rate =", str(i) + "%"
        filename = sys.argv[2]
        t1 = threading.Thread(target = server)
        t2 = threading.Thread(target = client)
        t1.start()
        time.sleep(2)
        t2.start()
        t2.join()
        t1.join()
        # extract the time out of the result
        y.append(float(''.join(re.findall(".+\nTime taken : (\d+)(\.)(\d+).+", out1)[0])))
    else :
        print "Go-back-%s with packet error rate ="  % (sys.argv[3]), str(i) + "%"
        global N
        N = sys.argv[3]
        filename = sys.argv[2]
        t1 = threading.Thread(target = server_gbn)
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
plt.xscale('log')
# plot
ax1 = fig.add_subplot(111)

# set graph parameters
ax1.set_title("Download time (in seconds) v/s Packet error rate (in %)")
ax1.set_xlabel('Packet error rate (in %)')
ax1.set_ylabel('Download time (in seconds)')

# point labelling
for xy in zip(x, y) :
    ax1.annotate('(%s, %s)' % xy, xy = xy, textcoords = 'data')

# plot with above set parameters
label = 'Download time v/s Packet error rate in Stop-and-Wait' if sys.argv[1] == "1" else 'Download time v/s Packet error rate in Go-back-N'
ax1.plot(x, y, 'bo-', c = 'r', label = label, linewidth = 2)
leg = ax1.legend(loc = 'upper left')

# show the graph
plt.show()