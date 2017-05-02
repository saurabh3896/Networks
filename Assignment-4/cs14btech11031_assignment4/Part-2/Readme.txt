Running on terminal :

    python proxy.py

This runs a proxy DNS server with IP = 127.0.0.1 and PORT = 5000.

In order to test the caching, two methods are there :

Method - 1 :

    python server.py [DOMAIN] [SERVER-IP] [SERVER-PORT]

Method - 2 :

    Run using 'nslookup' and test the caching. Command examples :

        nslookup -type=A www.google.com 127.0.0.1 -port=5000

        nslookup -type=NS www.google.com 127.0.0.1 -port=5000