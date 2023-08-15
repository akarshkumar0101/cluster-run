#!/bin/bash

while read server ; do
    echo "Connecting to server: $server"
    timeout 10 ssh $server.csail.mit.edu "uname -a" < /dev/null
    echo "Done with server: $server"
    echo
done < servers_all.txt