#include <cstdio>
#include <string>
#include <chrono>
#include <fcntl.h>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <iostream>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

using namespace std;

//packet structure including timestamp, eplased time for one trip and message buffer
struct timestamp {
  struct timeval current_time;
  long elapsed;
  char buffer[1024];
};

int main(int argc, char *argv[]){
  //variable declarations
  int socket_id, bytes_rcvd, num_messages, interval;
  size_t packet_size;
  socklen_t addr_size;
  std::string data_sent;
  char *buffer_rcvd;
  struct sockaddr_in server_addr, client_addr;
  //error checking
  if(argc != 4){
    cout << "Usage : " << argv[0] << " <interval> <number of messages> <packet size>\n";
    return 1;
  }
  //argument parsing
  interval = atoi(argv[1]);
  num_messages = atoi(argv[2]);
  packet_size = (size_t) atoi(argv[3]);
  buffer_rcvd = new char[packet_size];
  //create a new socket id
  if((socket_id = socket(AF_INET, SOCK_DGRAM, 0)) == -1){
    std::cerr << "Socket couldn't be created.\n";
    return 1;
  }
  //set the sockaddr struct parameters, including the addr family, port and IP
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(5000);
  server_addr.sin_addr.s_addr = INADDR_ANY;
  //initialize to 0
  memset(server_addr.sin_zero, '\0', sizeof(server_addr.sin_zero));
  addr_size = sizeof(struct sockaddr);
  //bind the socket to the given struct sockaddr
  if(bind(socket_id, (struct sockaddr *)&server_addr, addr_size) == -1){
      std::cerr << "Error in binding the socket as socket already in use.\n";
      return 1;
  }
  struct timeval get_time;
  for(int i = 0;i < num_messages;i++){
    struct timestamp rtt_struct;
    //get the bytes sent from the server
    int bytes_rcvd = recvfrom(socket_id, &rtt_struct, sizeof(rtt_struct), 0, (struct sockaddr *) &client_addr, &addr_size);
    get_time = rtt_struct.current_time;
    cout << "Received at server : ";
    cout << rtt_struct.buffer << endl;
    //get the current_time
    gettimeofday(&rtt_struct.current_time, 0);
    rtt_struct.elapsed = (rtt_struct.current_time.tv_sec - get_time.tv_sec) * 1000000
     + rtt_struct.current_time.tv_usec - get_time.tv_usec;
    //send the bytes to the server
    int bytes_sent = sendto(socket_id, &rtt_struct, sizeof(rtt_struct), 0, (struct sockaddr *) &client_addr, addr_size);
  }
  return 0;
}
