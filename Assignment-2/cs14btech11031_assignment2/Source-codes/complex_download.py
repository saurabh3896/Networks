import os, sys, time, socket, hashlib, urlparse, StringIO, mimetools, subprocess
from threading import Thread

# error handling in case of incorrect command-line arguments
if len(sys.argv) != 3 :
    print "Usage : python client.py [URL] [n]"
    exit(0)

# store the command-line arguments
url, no_of_connections, cr_lf = sys.argv[1], int(sys.argv[2]), '\r\n\r\n'

def get_range(file_size, n_threads) :
    # get the lenght of each chunk, which is equal for all threads
    step_size = (int(file_size))/float(n_threads)
    # generate a continuous series of ranges, like 0-100, 101-200, ...
    final_list = ["%s-%s" % (0, int(round(i*step_size + step_size))) if i is 0
    else "%s-%s" % (int(round(1 + i*step_size)), int(round(i*step_size + step_size)))
    for i in range(n_threads)]
    return final_list

def parse_size(size) :
    # get the file size in appropriate UNIT
    end, count, size = ['B', 'KB', 'MB', 'GB'], 0, int(size)
    while size >= 1024.0 and count < len(end) - 1 :
        # divide by 1024 unless size < 1024
        size /= 1024.0
        count += 1
    return ("%.2f" % size).rstrip('0').rstrip('.') + " " + end[count]

# function to separate headers from the downloaded stream
def get_response_header(sock) :
    data = ''
    # keep capturing unless CRLF encountered
    while '\r\n\r\n' not in data :
        part = sock.recv(1024)
        if not part :
            # socket closed
            break
        data += part
    # the remaining is some chunk just after the CRLF, the only data of interest
    header, boundary, remaining = data.partition('\r\n\r\n')
    return header, remaining

def parse(a) :
    # parse string of the format %s-%s to get the difference between the two %s's
    a = a.split("-")
    # return the difference
    return int(a[1]) - int(a[0])

thread_data, file_size, parsed_url = {}, None, urlparse.urlparse(url)

def thread_download(thread_no, byte_range) :
    # create a new socket
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # create a raw HTTP GET request
    header_lines = [
     "GET %s HTTP/1.1" % (url),
     "Host: %s" % (host),
     "Range: bytes=%s" % (byte_range)
    ]
    # join the contents of the above list to formulate the GET request
    get_request = "\r\n".join(header_lines) + "\r\n\r\n"
    # connect to the server and bind to port 80
    socket_id.connect((host, 80))
    # measure the starting time for calculating RTT
    start = time.time()
    # send the above formulated GET request
    socket_id.sendall(get_request)
    response, remaining = get_response_header(socket_id)
    # after separating headers, initialize loop counters
    cur_size, thread_data[thread_no], content_length = len(remaining), remaining, parse(byte_range)
    #thread_data[thread_no] += socket_id.recv(content_length + 10000, socket.MSG_WAITALL)
    while cur_size < content_length :
        # keep receiving data unless the specified chunk is completely downloaded
        test = socket_id.recv(1000000)
        # append the downloaded data into the dictionary field containing every thread's data as a value with the thread_no being the key
        thread_data[thread_no] += test
        # update the loop counter
        cur_size = len(thread_data[thread_no])
        # throughput is total captured bytes by total time passed by now (time is basically RTT for each socket.recv() call)
        ins_throughput = float(cur_size)/(time.time() - start)
        ins_throughput /= 1024.0
        # uncomment the below line to print instantaneous throughput for each thread/stream
        #print "Throughput for thread %d : %.2f bytes/sec" % (thread_no, ins_throughput)
    # close the socket
    socket_id.shutdown(1)
    socket_id.close()

url_path, host = parsed_url.path, parsed_url.netloc
# formulate a HEAD request
header_lines = [
 "HEAD %s HTTP/1.1" % (url),
 "Host: %s" % (host)
]
# join the contents of the above list to formulate the HEAD request
head_request = "\r\n".join(header_lines) + "\r\n\r\n"
# create a new socket
socket_id = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try :
    # connect to the server and bind to port 80
    socket_id.connect((host, 80))
    # send the above formulated HEAD request to the server for querying file size
    socket_id.send(head_request)
    # get the server's response
    recv_head = socket_id.recv(1024)
except socket.error, e :
    # handle exceptions here
    print "Exception caught socket.error : %s" % e

request_line, headers_alone = recv_head.split('\r\n', 1)
# headers parsing
headers = mimetools.Message(StringIO.StringIO(headers_alone))

# error handling in case of Non-OK response from the server
if "200" not in request_line :
    print "Download failed. Please try a different URL, Error code :", request_line[9:]
    exit(1)

# error handling in case of bad request
if 'content-length' not in headers.keys() :
    print "Nothing to download, please try a different URL."
    exit(0)

# error handling if file not downloadable, present on the server or its size is 0
file_size = headers['Content-Length']
if file_size == 0 :
    print "Nothing to download (content-type : 'text/html' or similar), please try a different URL."
    exit(0)

# print the file size
print "The file size is %s bytes (%s)." % (file_size, parse_size(file_size))
# close the socket
socket_id.shutdown(1)
socket_id.close()

# spawn N threads and dispatch each thread to download byte_range number of bytes
threadpool = [Thread(target = thread_download, args = (i, byte_range)) for i, byte_range in enumerate(get_range(file_size, no_of_connections))]

# record the current time
start_time = time.time()

# start all the threads
for thread in threadpool :
    thread.start()
# join all the threads once they finish their execution
for thread in threadpool :
    thread.join()

# get the filename of original file
filename_ = url.split("/")[-1]
# filename of the downloaded file
filename = "download_" + filename_
# sort the dictionary containing each thread's data in order to assemble the original file
final_data = sorted(thread_data.iteritems())
with open(filename, 'wb') as fh :
    # write every chunk to the final downloaded file
    for i, part in final_data :
        fh.write(part)

# indicate that file downloading has been finished
print "\nFinished downloading file '%s'." % (filename)
# print the size of the downloaded file, and can be compared with the file size got from the server printed earlier
print 'Downloaded file size : %s bytes.' % (os.path.getsize(filename))

# print the time taken for download
print "Time taken : %s seconds." % str(time.time() - start_time)

# perform checksum check using 'sha256' secure hash algorithm
print "Checksum check using 'sha256' secure hash algorithm :"
print "====================================================="
original, downloaded =  hashlib.sha256(open(filename_, 'rb').read()).digest(),  hashlib.sha256(open(filename, 'rb').read()).digest()
print "Downloaded file not corrupted !" if original == downloaded else "Downloaded file corrupted !"