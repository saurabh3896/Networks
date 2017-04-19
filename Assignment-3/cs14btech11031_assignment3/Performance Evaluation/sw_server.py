import os, socket, sys, struct, thread, time, math

if len(sys.argv) != 2 :
    print "Usage : python server.py [FILENAME]"
    exit(0)

def get_ack_no(packet) :
    return int(packet[3]) if packet[:3] == "ACK" else -1

def carry_around_add(a, b) :
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg) :
    s = 0
    if len(msg) % 2 != 0 :
         msg += "\x00"
    for i in range(0, len(msg), 2) :
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def get_packet(seq_num, payload, put) :
    header = struct.pack('HHL', seq_num, 0, 0)
    my_checksum = checksum(header + payload)
    if put == "first" :
        length = os.path.getsize(filename)
    else :
        length = len(payload)
    header = struct.pack('HHL', seq_num, my_checksum, length)
    return header + payload

try :
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

filename, seq_num, ack_num, address = sys.argv[1], 0, None, (socket.gethostbyname("0.0.0.0"), 5000)

socket_id.bind(address)

SampleRTT, EstRTT = 1, 1
# set initial timeout here
socket_id.settimeout(EstRTT)

while True :
    try :
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

packet = get_packet(seq_num, filename, "first") + "||"

while True :
    start = time.time()
    socket_id.sendto(packet, address)

    while True :
        try :
            recv_packet, address = socket_id.recvfrom(1024)
            end = time.time()
            SampleRTT = end - start
            EstRTT = 0.875*EstRTT + 0.125*SampleRTT
            # set the timeout here to 3*EstRTT
            socket_id.settimeout(3*EstRTT)
            ack_num = get_ack_no(recv_packet)
            if seq_num == ack_num :
                print "Packet with sequence number", seq_num, "delivered !"
                break
            else :
                print "ACK not equal to SEQ or data corrupted !"
        except socket.timeout :
            print "Timeout occured ! Resending packet ..."
            start = time.time()
            socket_id.sendto(packet, address)

    data = fp.read(1000)
    if data == '' :
        packet = "END"
        socket_id.sendto(packet, address)
        print "File transfer complete. Server now shutting down."
        break
    seq_num = (seq_num + 1) % 2
    packet = get_packet(seq_num, data, "not_first")

socket_id.close()
fp.close()