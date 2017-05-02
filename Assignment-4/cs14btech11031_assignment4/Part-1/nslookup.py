import os, re, sys, time, math, socket, struct, thread, random

def get_dns_type(dns_type) :
	# dictionary defining the code for each dns_request_type
	dns_type_dict = {1 : 'A', 2 : 'NS', 5 : 'CNAME', 6 : 'SOA'}
	return dns_type_dict.get(dns_type, 'A')

def parse_value(w) :
	# method for parsing the header contents
	result = ord(w[0])
	temp = list(w)
	del temp[0]
	w = ''.join(temp)
	# get the ascii and shift to next byte
	while w :
		add_step = ord(w[0])
		result = 256 * result
		# multiply by 256 and add the next byte
		result += add_step
		temp = list(w)
		del temp[0]
		w = ''.join(temp)
	return result

def next_offset(size, next_byte) :
	return ((size & 63) << 8) + next_byte

def len_dom(res, index) :
	# method for providing the length of the domain parts recursively
	get_size = ord(res[index])
	test1, test2 = get_size is 0, get_size > 63
	if test1 :
		return 1
	elif test2 :
		return 2
	else :
		return get_size + 1 + len_dom(res, index + 1 + get_size)

def parse_url(res, index = 0) :
	# method to get the domain name
	get_size = ord(res[index])
	test1, test2 = get_size is 0, get_size < 63
	if test1 :
		# recursion reached end at null string
		return ''
	elif test2 :
		name, rest = res[index + 1:index + 1 + get_size], parse_url(res, index + 1 + get_size)
		# concatenate the two parts separated by a '.'
		return name + "." + rest if rest else name
	step = next_offset(get_size, ord(res[index + 1]))
	# recur on the next step (offset)
	return parse_url(res, step)

def get_domain_details(res, index) :
	temp = index
	index += len_dom(res, temp)
	# parsing time-to-live and other fields from the given response
	ttl, l, o = parse_value(res[index + 4:index + 8]), parse_value(res[index + 8:index + 10]), index + 10
	return (len_dom(res, temp) + 10 + l, parse_url(res, temp),
	get_dns_type(parse_value(res[index:index + 2])), parse_value(res[index + 2:index + 4]), ttl, (l, o))

def parse_dns_response(res, index = 0) :
	# the header is the firs 12 bytes of the response, parsing various parts accordingly
	header = (parse_value(res[index:index + 2]), (1, 0, 0, 0, 1, 1, 0), parse_value(res[index + 4:index + 6]),
	parse_value(res[index + 6:index + 8]), parse_value(res[index + 8:index + 10]), parse_value(res[index + 10:index + 12]))
	# set j = 12 since headers are extracted, so j is the new offset
	count, i, j, queries = header[2], 0, 12, []
	while i < count :
		# get the sub dns_type and sub dns_class
		dns_type_ = parse_value(res[j + len_dom(res, j):j + len_dom(res, j) + 2])
		dns_class_ = parse_value(res[j + len_dom(res, j) + 2:j + len_dom(res, j) + 4])
		if dns_class_ != 1 :
			print "** server can't find %s: NXDOMAIN\n" % (sys.argv[1])
			exit(1)
		(size, domain, dns_type, dns_class) = (len_dom(res, j) + 4, parse_url(res, j), dns_type_, dns_class_)
		queries.append((domain, dns_type, dns_class))
		i += 1
		j += size
	# get the answer count from the sum of some header contents
	i, answers, count = 0, [], header[3] + header[4] + header[5]
	while i < count :
		(size, domain, dns_type, dns_class, ttl, (length, step)) = get_domain_details(res, j)
		if dns_type == 'A' :
			# if DNS type is 'A'
			data = res[step:step + length]
			ip_address = tuple(map(ord, (data[0], data[1], data[2], data[3])))
			data = '%d.%d.%d.%d' % ip_address
		elif dns_type in ['NS', 'CNAME'] :
			# same method for CNAME and NS types
			data = parse_url(res, step)
		elif dns_type == 'SOA' :
			# invalid domain error reporting
			print "** server can't find %s: NXDOMAIN\n" % (sys.argv[1])
			exit(1)
		else :
			continue
		# appending the IP addresses and Canonical names in the output result array
		answers.append((domain, dns_type, dns_class, ttl, data))
		j += size
		i += 1
	return (header, queries, answers)

def encode_hex(arg) :
	# method for encoding the argument into hex value
	return struct.pack('L', arg)

if len(sys.argv) not in [3, 4, 5, 6] :
    # error handling
	print "Usage : python nslookup.py [DOMAIN] [DNS-SERVER-ADDRESS] {-type='A/NS'} {-timeout=value} {-port=value}"
	exit(0)

try :
    # create a new socket
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

domain_name, dns_server_address = sys.argv[1], sys.argv[2]
# regex for matching a valid hostname taken from http://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address
pattern = re.compile(r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
if not pattern.match(sys.argv[1]) :
	print "nslookup: '%s' is not a legal name (empty label)" % domain_name
	exit(1)

arg_dict = {}
for i in range(3, len(sys.argv)) :
	# argument parsing
	get = sys.argv[i]
	val = get[1:get.index('=')]
	arg_dict[val] = get[get.index('=') + 1:]
port, timeout, dns_query_type = int(arg_dict.get('port', 53)), int(arg_dict.get('timeout', 15)), arg_dict.get('type', 'A')

try :
	# connect with the DNS server with the specified port (default = 53)
    socket_id.connect((dns_server_address, port))
except Exception as e :
    print "something's wrong with %s:%d. Exception is %s" % (dns_server_address, port, e)

print "Server:		" + dns_server_address
print "Address:        " + dns_server_address + "#%d\n" % (port)

# adding random header ID
get_request_id = bytearray(encode_hex(1234))[:2]
get_request_id.reverse()
dns_request = get_request_id
# adding flags
flags = bytearray(encode_hex(256))[:2]
flags.reverse()
dns_request += flags
# adding qdcount
var = bytearray(encode_hex(1))[:2]
var.reverse()
dns_request += var
# adding ancount
var = bytearray(encode_hex(0))[:2]
var.reverse()
dns_request += var
# adding nscount
var = bytearray(encode_hex(0))[:2]
var.reverse()
dns_request += var
# adding arcount
var = bytearray(encode_hex(0))[:2]
var.reverse()
dns_request += var

# make the string like 3www5gmail3com if the domain name is www.gmail.com
for i in domain_name.split(".") :
    domain_len_part = bytearray(encode_hex(len(i)))[:1]
    domain_len_part.reverse()
    dns_request += domain_len_part
    dns_request += bytearray(i)

var = bytearray(encode_hex(0))[:1]
var.reverse()
dns_request += var
# adding Qtype to the response
var = bytearray(encode_hex(1))[:2]
var.reverse()
dns_request += var
# adding QClass to the response
var = bytearray(encode_hex(1))[:2]
var.reverse()
dns_request += var

try :
	# send the complete response to the DNS server
    socket_id.sendall(dns_request)
except Exception as e :
    print e

# setting the timeout on the receiving socket
socket_id.settimeout(timeout)

try :
	# receive the DNS server's response here
	get_response = socket_id.recv(512)
except socket.timeout as e :
	print ";; connection timed out; no servers could be reached"
	exit(0)

# parse the DNS server response
final = parse_dns_response(get_response)
responses = final[2]

# print Authoritative or Non-authoritative answers depending on the type
print "Non-authoritative answer:" if dns_query_type is 'A' else "Authoritative Name Servers:"

if dns_query_type == 'NS' :
	for i in responses :
		if 'NS' in i :
			# print the Name-servers
			print "origin = " + i[-1]
	print
	exit(0)

for i in responses :
	if 'CNAME' in i :
		# Canonical name case
		print i[0] + "\t" + "canonical name = " + i[-1] + "."
	elif 'A' in i :
		# print the name and the corresponding IP address
		print "Name:\t" + i[0]
		print "Address: " + i[-1]
	elif 'NS' in i :
		break
print
