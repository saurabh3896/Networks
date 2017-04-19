import os, socket, sys, struct, thread, time, math

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

def corrupt(packet) :
    seq_num, terminate, check_sum, length = struct.unpack('HHHL', packet[:16])
    header_new = struct.pack('HHHL', seq_num, terminate, 0, 0)
    return check_sum != checksum(header_new + packet[16:])

try :
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

address, expectedseqnum, end = ("", 5000), 0, False

# dummy request to server to indicate that the client is requesting the server to download a file
socket_id.sendto("Request", address)

download_start = time.time()

while not end :
    try :
        data, address = socket_id.recvfrom(4096)
        recv_packet, content = struct.unpack('HHHL', data[:16]), data[16:]
        seq_num, terminate, check_sum, length = recv_packet[0], recv_packet[1], recv_packet[2], recv_packet[3]
        if seq_num == expectedseqnum and not corrupt(data) :
            expectedseqnum += 1
            if data[-1] == "|" and data[-2] == "|" :
                file_name = "rcvd_" + data[16:len(data) - 2]
                try :
                    os.remove(file_name)
                except OSError :
                    pass
                fp = open(file_name, "wb")
                file_size = length
                print "File '" + file_name + "' with file size", file_size, "bytes opened for downloading !"
            else :
                fp.write(content)
                print "Packet with sequence number", seq_num, "received !"
            end = terminate
        else :
            print "Packet with sequence number", seq_num , "discarded (corrupted or not in order) !"
        print "Sending ACK numbered", expectedseqnum - 1, "to the server ..."
        socket_id.sendto("ACK" + str(expectedseqnum - 1), address)
    except Exception as e :
        print "Exception :", e
        pass

socket_id.close()
fp.close()
print "File download complete. Downloaded file size is", os.path.getsize(file_name), "bytes."

# print the time taken for download
print "Time taken : %s seconds." % str(time.time() - download_start)