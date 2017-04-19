import os, socket, sys, struct, thread, time, math

if len(sys.argv) != 3 :
    # error handling
    print "Usage : python server.py [FILENAME] [N]"
    exit(0)

def get_ack_no(packet) :
    # get the ACK number
    return int(packet[3:]) if packet[:3] == "ACK" else -1

def carry_around_add(a, b) :
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg) :
    # checksum function
    s = 0
    if len(msg) % 2 != 0 :
         msg += "\x00"
    for i in range(0, len(msg), 2) :
        # calculate byte sum
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def get_packet(seq_num, payload, put) :
    terminate = True if seq_num == num_of_packets - 1 else False
    header = struct.pack('HHHL', seq_num, terminate, 0, 0)
    # calculate checksum here
    my_checksum = checksum(header + payload)
    if put == "first" :
        length = file_size
    else :
        length = len(payload)
    # create the packet here
    header = struct.pack('HHHL', seq_num, terminate, my_checksum, length)
    return header + payload

try :
    # create a socket here
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

filename, N, address = sys.argv[1], int(sys.argv[2]), (socket.gethostbyname("0.0.0.0"), 5000)

socket_id.bind(address)

SampleRTT, EstRTT = 1, 1
# set initial timeout here
socket_id.settimeout(1)

while True :
    try :
        # confirmation that client is requesting a file download
        test_recv, address = socket_id.recvfrom(1024)
        print "Client requested the server to download the file !"
        break
    except socket.timeout as e :
        print "Waiting for the client to send a request ..."
        continue

try :
    fp = open(filename, "rb")
except IOError as e :
    print "Error : " + str(e)[10:] + ". Please enter a valid filename."
    exit(0)

file_size = os.path.getsize(filename)
sndpkt, base, nextseqnum, num_of_packets = [], 0, 0, int(math.ceil(file_size/1000.0)) + 1

while True :
    enter = 0
    while nextseqnum < base + N and nextseqnum < num_of_packets :
        # send packets until the window is not full
        enter += 1
        data = filename + "||" if base is 0 and nextseqnum is 0 else fp.read(1000)
        # create a new packet here
        packet = get_packet(nextseqnum, data, "first") if base is 0 and nextseqnum is 0 else get_packet(nextseqnum, data, "not_first")
        sndpkt.append(packet)
        print "Sending packet with sequence number", nextseqnum, "and size", len(data), "!"
        while True :
            try :
                # send the packet here
                start = time.time() if enter is 1 else start
                socket_id.sendto(packet, address)
                break
            except socket.timeout as e :
                continue
        # increase the nextseqnum
        nextseqnum += 1

    try :
        # receive ACK from the client
        recv_packet, address = socket_id.recvfrom(1024)
        end = time.time()
        SampleRTT = end - start
        # exponential average to estimate timeout
        EstRTT = 0.875*EstRTT + 0.125*SampleRTT
        # set the timeout here to 3*EstRTT
        socket_id.settimeout(3*EstRTT)
        ack_num = get_ack_no(recv_packet)
        if ack_num + 1 == num_of_packets :
            # correct ACK and transfer complete
            print "File transfer complete. Server now shutting down."
            break
        if ack_num == -1 :
            # packet is corrupted
            print "Packet received is corrupted !"
        else :
            # ACK correct and not corrupted
            print "ACK numbered", ack_num, "received from client !"
            base = ack_num + 1
    except socket.timeout :
        print "Timeout occured ! Resending packets' number ranging from", base, "to", nextseqnum - 1
        for i in range(base, nextseqnum) :
            print "Sending packet with sequence number", i, "and size", len(sndpkt[i]), "!"
            while True :
                try :
                    # Uncomment in case of proper simulation
                    #start = time.time() if i == base else start
                    socket_id.sendto(sndpkt[i], address)
                    break
                except socket.timeout as e :
                    # timeout handling if sending is too fast, timeout maintained in such a way that this doesn't happen
                    continue

socket_id.close()
fp.close()