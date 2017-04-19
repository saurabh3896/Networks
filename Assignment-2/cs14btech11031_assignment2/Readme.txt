The following are the contents of this assignment :

1. Source-codes : This folder contains all the source codes for both downloading and plotting the graph.
2. Report : Report.pdf
3. Readme.txt

-----------------------------------------------------------------------------------------------------------------------------

Running of the code for downloading the file :

  python download.py [URL] [N]

  For perfoming the checksum test, make sure that the downloaded file (original) and the one downloaded using the code are in
  the same directory.

Running of the code for plotting the graph of download-times v/s the number of connections made :

  python analyze.py [URL]

  This code runs the main source code for downloading file by varying the number of parallel connections made to the server. The
  values, N, takes are 1, 3, 5, 7, 9 and 14. The X-axis represents the values of N and the Y-axis, the corresponding download time
  taken.

Note :

An additional code, named, "complex_download.py", is provided as well, which is made for handling 400 Bad Requests, and sends
the complete URL as the file path in the GET and HEAD requests. Only shortcoming in this code is that in order to handle bad requests,
no URL parsing is done, hence the file name of the downloaded file may be gibberish, and may also need to be supplied with a correct
extension, only in rare cases though.