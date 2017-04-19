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

int main(int argc, char *argv[]){
  //variable declaration
  int socket_id;
  size_t packet_size;
  ssize_t bytes_rcvd, bytes_sent;
  socklen_t addr_size;
  char *buffer_rcvd;
  struct sockaddr_in server_addr, client_addr;
  //error handling
  if(argc != 2){
    cout << "Usage : " << argv[0] << " <packet size>\n";
    return 1;
  }
  //argument parsing
  packet_size = (size_t) atoi(argv[1]);
  buffer_rcvd = new char[packet_size];
  //create a new socket and the get the socket_id
  if((socket_id = socket(AF_INET, SOCK_DGRAM, 0)) == -1){
    std::cerr << "Socket couldn't be created.\n";
    return 1;
  }
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(5000);
  server_addr.sin_addr.s_addr = INADDR_ANY;
  memset(server_addr.sin_zero, '\0', sizeof(server_addr.sin_zero));
  addr_size = sizeof(struct sockaddr);
  //bind the socket
  if(bind(socket_id, (struct sockaddr *)&server_addr, addr_size) == -1){
      std::cerr << "Error in binding the socket as socket already in use.\n";
      return 1;
  }
  while(1){
    //get the bytes sent from the client
    bytes_rcvd = recvfrom(socket_id, buffer_rcvd, sizeof(buffer_rcvd), 0, (struct sockaddr *) &client_addr, &addr_size);
    buffer_rcvd[bytes_rcvd] = 0;
    cout << "Message received at server : " << buffer_rcvd << endl;
    //send the packet back to the client
    bytes_sent = sendto(socket_id, buffer_rcvd, sizeof(buffer_rcvd), 0, (struct sockaddr *) &client_addr, addr_size);
  }
  return 0;
}
