This directory contains three scripts, which using the Linux's "tc" tool, simulate packet corruption for Part-a,
packet delay + loss for Part-b and packet loss + delay, along with varying N in GBN for Part-c and generate graphs.

The tool used in "tc", which a network-traffic manipulation tool, just like ethtool. The three scripts output graphs
depending on the command-line arguments in each of the parts.

A copy of all the server and client codes is in this directory for faciliating the graph making.

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

PART-A
------

Command :

  To get a graph for Stop-and-wait :

  python a_script.py 1 [FILENAME]

  To get a graph for Go-back-N :

  python a_script.py 2 [FILENAME] [N]

  Here, FILENAME is the name of the file being transmitted, in the same directory.

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

PART-B
------

Command :

  To get a graph for Stop-and-wait :

  python b_script.py 1 [FILENAME]

  To get a graph for Go-back-N :

  python b_script.py 2 [FILENAME] [N]

  Here, FILENAME is the name of the file being transmitted, in the same directory.

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

PART-C
------

Command :

  Getting a graph for Go-back-N :

  python c_script.py [FILENAME]