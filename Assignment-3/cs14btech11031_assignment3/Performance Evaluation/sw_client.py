import os, socket, sys, struct, thread, time, math

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
    if packet[-1] == '|' and packet[-2] == '|' :
        return False
    seq_num, check_sum, length = struct.unpack('HHL', packet[:16])
    header_new = struct.pack('HHL', seq_num, 0, 0)
    return check_sum != checksum(header_new + packet[16:])

try :
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

address, ack_num = ("", 5000), 0

# dummy request to server to indicate that the client is requesting the server to download a file
socket_id.sendto("Request", address)

download_start = time.time()

while True :
    try :
        data, address = socket_id.recvfrom(4096)
        if data == "END" :
            break
        recv_packet, content = struct.unpack('HHL', data[:16]), data[16:]
        seq_num, check_sum, length = recv_packet[0], recv_packet[1], recv_packet[2]
        if corrupt(data) or ack_num != seq_num :
            send_seq_num = 1 if ack_num is 0 else 0
            socket_id.sendto("ACK" + str(send_seq_num), address)
            print "ACK not equal to SEQ or data corrupted !"
        elif data[-1] == "|" and data[-2] == "|" :
            file_name = "rcvd_" + data[16:len(data) - 2]
            try :
                os.remove(file_name)
            except OSError :
                pass
            fp = open(file_name, "wb")
            file_size = length
            print "File '" + file_name + "' with file size", file_size, "bytes opened for downloading !"
            ack_num = (ack_num + 1) % 2
            print "Sending ACK numbered", ack_num, "to the server ..."
            socket_id.sendto("ACK" + str(seq_num), address)
        elif not corrupt(data) and ack_num == seq_num :
            fp.write(content)
            ack_num = (ack_num + 1) % 2
            print "Sending ACK numbered", ack_num, "to the server ..."
            socket_id.sendto("ACK" + str(seq_num), address)
    except Exception as e :
        print "Exception :", e
        pass

socket_id.close()
fp.close()
print "File download complete. Downloaded file size is", os.path.getsize(file_name), "bytes."

# print the time taken for download
print "Time taken : %s seconds." % str(time.time() - download_start)