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

void currentTime(char buf[]){                                   //function to return current time in standard format
  time_t now = time(NULL);                                      //get the current time
  struct tm tstruct;                                            //time struct
  tstruct = *localtime(&now);                                   //store current time into struct
  char buffer[80];                                              //declare a char buffer to store timestamp
  strftime(buffer, sizeof(buffer), "%X", &tstruct);             //print in standard format
  strcpy(buf, buffer);
}

int main(int argc, char *argv[]){
  //variable declaration
  int socket_id, interval, no_of_packets = 1, trip = 0, count = 1;
  double total_time = 0, throughput, average_delay = 0;
  size_t packet_size;
  ssize_t bytes_rcvd, bytes_sent, total_size = 0;
  socklen_t addr_size;
  char *buffer_rcvd;
  struct sockaddr_in server_addr;
  struct timeval t0, t1;
  //open files to store readings for throughput and average_delay
  FILE *fp = fopen("output1.txt", "a+");
  FILE *fp_ = fopen("output2.txt", "a+");
  //error handling
  if(argc != 3){
    cout << "Usage : " << argv[0] << " <interval> <packet size>\n";
    return 1;
  }
  //argument parsing
  interval = atoi(argv[1]);
  packet_size = (size_t) atoi(argv[2]);
  buffer_rcvd = new char[packet_size];
  //create a new socket and get the socket_id
  if((socket_id = socket(AF_INET, SOCK_DGRAM, 0)) == -1){
    std::cerr << "Socket couldn't be created.\n";
    return 1;
  }
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(5000);
  server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  memset(server_addr.sin_zero, '\0', sizeof(server_addr.sin_zero));
  addr_size = sizeof(struct sockaddr);
  //while interval is positive, send multiple packets
  while(interval > 0){
    //send no_of_packets number of packets
    for(int i = 0;i < no_of_packets;i++){
      currentTime(buffer_rcvd);
      gettimeofday(&t0, 0);
      //send the packets to the server
      bytes_sent = sendto(socket_id, buffer_rcvd, sizeof(buffer_rcvd), 0, (struct sockaddr *) &server_addr, addr_size);
      buffer_rcvd[bytes_sent] = '\0';
      //get the packets send from the server
      bytes_rcvd = recvfrom(socket_id, buffer_rcvd, sizeof(buffer_rcvd), 0, (struct sockaddr *) &server_addr, &addr_size);
      //get the currentTime
      gettimeofday(&t1, 0);
      cout << "Received message on trip " << trip << " : " << buffer_rcvd << endl;
      total_size += bytes_sent;
      //time calculation
      total_time += ((t1.tv_sec - t0.tv_sec) * 1000000
       + t1.tv_usec - t0.tv_usec);
      total_time /= 1000000.0;
      throughput += (total_size)/total_time;
      double temp = total_time * 1000;
      average_delay = temp/count++;
      //output the readings to the files
      for(int j = 0;j < interval;j++){
        fprintf(fp, "%lf\n", throughput);
        fprintf(fp_, "%lf\n", average_delay);
      }
    }
    //increment counters
    no_of_packets++, trip++;
    //decrease sleep interval
    sleep(interval--);
  }
  return 0;
}
