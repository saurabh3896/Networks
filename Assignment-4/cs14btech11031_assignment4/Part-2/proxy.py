import os, re, sys, time, math, socket, struct, thread, random

def next_offset(size, next_byte) :
	# take bitwise AND with 63 and multiply by 2^8
	return ((size & 63) << 8) + next_byte

def parse_value(w) :
	# parsing the contents of the header
	result = ord(w[0])
	temp = list(w)
	del temp[0]
	w = ''.join(temp)
	while w :
		add_step = ord(w[0])
		result = 256 * result
		result += add_step
		temp = list(w)
		del temp[0]
		w = ''.join(temp)
	return result

def len_dom(res, index) :
	get_size = ord(res[index])
	test1, test2 = get_size is 0, get_size > 63
	if test1 :
		return 1
	elif test2 :
		return 2
	else :
		return get_size + 1 + len_dom(res, index + 1 + get_size)

# method for parsing url recursively
def parse_url(res, index = 0) :
	get_size = ord(res[index])
	test1, test2 = get_size is 0, get_size < 63
	if test1 :
		return ''
	elif test2 :
		name, rest = res[index + 1:index + 1 + get_size], parse_url(res, index + 1 + get_size)
		return name + "." + rest if rest else name
	step = next_offset(get_size, ord(res[index + 1]))
	return parse_url(res, step)

try :
    # create a new socket
    socket_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e :
    print "Socket creation failed, probably already in use."
    exit(0)

# running server on this address
dns_server_address = ('127.0.0.1', 5000)
socket_id.bind(dns_server_address)

# defining dictionary for dns types
cache, type_dict = {}, {1 : 'A', 2 : 'NS'}

while True :
	# receive the query from client
	recv_query, address = socket_id.recvfrom(512)
	dns_type = parse_value(recv_query[12 + len_dom(recv_query, 12):12 + len_dom(recv_query, 12) + 2])
	# get the domain name for key requried for caching
	domain_name = parse_url(recv_query, 12)
	# create a socket for forwarding this request to the local DNS server
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if domain_name + "|" + type_dict[dns_type] in cache :
		# if the query is cached
		print "Domain name %s, type=%s was cached !" % (domain_name, type_dict[dns_type])
		get = recv_query[:2] + cache[domain_name + "|" + type_dict[dns_type]][2:]
		socket_id.sendto(get, address)
	else :
		# else request the server to respond for the given query
		sock.connect(('127.0.1.1', 53))
		sock.sendall(recv_query)
		query_local_dns = sock.recv(512)
		key = domain_name + "|" + type_dict[dns_type]
		# cache the DNS query
		cache[key] = query_local_dns
		socket_id.sendto(cache[key], address)
		print "Query for domain %s, type=%s processed !" % (domain_name, type_dict[dns_type])
