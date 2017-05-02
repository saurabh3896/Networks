Running on terminal :

    python nslookup.py [DOMAIN] [DNS-SERVER-ADDRESS] {-type='A/NS'} {-timeout=value} {-port=value}

The first TWO arguments in square brackets are mandatory, the FIRST argument being the domain name, the SECOND argument
being the DNS-server address.

The rest of the arguments in curly brackets are optional, and need to be entered exactly as shown in the above command.

Examples :

    python nslookup.py www.google.com 192.168.35.52 -timeout=10 -port=53

    python nslookup.py www.google.com 192.168.35.52 -port=53 -type=NS

    python nslookup.py www.google.com 192.168.35.52 -type=A -timeout=10

    python nslookup.py www.google.com 192.168.35.52 -timeout=10 -port=53 -type='A'