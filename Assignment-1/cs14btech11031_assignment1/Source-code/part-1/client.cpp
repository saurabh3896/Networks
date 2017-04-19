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

void currentTime(char buf[]){                                   //function to return current time in standard format
  time_t now = time(NULL);                                      //get the current time
  struct tm tstruct;                                            //time struct
  tstruct = *localtime(&now);                                   //store current time into struct
  char buffer[80];                                              //declare a char buffer to store timestamp
  strftime(buffer, sizeof(buffer), "%X", &tstruct);             //print in standard format
  strcpy(buf, buffer);
}

int main(int argc, char *argv[]){
  //variable declarations
  int socket_id, bytes_rcvd, num_messages, interval, lost_packets = 0;
  size_t packet_size;
  socklen_t addr_size, ntrcv = sizeof(struct timeval);
  std::string data_sent;
  char *buffer_rcvd;
  struct sockaddr_in server_addr;
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
  server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  addr_size = sizeof(struct sockaddr);
  //initialize to 0
  memset(server_addr.sin_zero, '\0', sizeof(server_addr.sin_zero));
  struct timeval tv;
  tv.tv_sec = 0;
  tv.tv_usec = 100000;
  struct timeval get_final;
  long rtt;
  //loop over the given number of packets
  for(int i = 0;i < num_messages;i++){
    struct timestamp rtt_struct, new_rtt_struct;
    //get the current_time
    gettimeofday(&rtt_struct.current_time, 0);
    rtt_struct.elapsed = 0;
    currentTime(rtt_struct.buffer);
    //send the bytes to the server
    int bytes_sent = sendto(socket_id, &rtt_struct, sizeof(rtt_struct), 0, (struct sockaddr *) &server_addr, addr_size);
    if(setsockopt(socket_id, SOL_SOCKET, SO_SNDTIMEO, (char *) &tv, sizeof(struct timeval)) < 0){
      perror("Error in setting socket options\n");
    }
    //get the received bytes
    int bytes_rcvd = recvfrom(socket_id, &new_rtt_struct, sizeof(new_rtt_struct), 0, NULL, NULL);
    gettimeofday(&get_final, 0);
    //lost packets error handling
    if(bytes_rcvd < 0){
      std::cout << "Timeout occured." << endl;
      lost_packets++;
      continue;
    }
    //elpased rtt calculation
    rtt = (get_final.tv_sec - new_rtt_struct.current_time.tv_sec) * 1000000
     + get_final.tv_usec - new_rtt_struct.current_time.tv_usec;
    rtt += new_rtt_struct.elapsed;
    cout << "Received at client : ";
    cout << new_rtt_struct.buffer;
    cout << " | Round-trip-time : " << rtt << " us" << endl;
    //cout << "Second-round-trip-time : " << (-rtt_struct.current_time.tv_sec + get_final.tv_sec) * 1000000
    // + get_final.tv_usec - rtt_struct.current_time.tv_usec  << " us" << endl; / *for checking purposes */
    sleep(interval);
  }
  //print the packet loss %
  cout << "Packet loss : " << (lost_packets)/num_messages << "%\n";
  return 0;
}
