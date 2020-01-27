Simple ping program using python

To run:
Open up the terminal and change to the current directory which holds the python file.
To run and connect, enter the command " sudo python ping.py -enter a URL- ", replacing the -enter a URL- with a website address that you want to do a ping test with.
From there the program is running and will continuously send and receive a ping packet, printing out a formatted ICMP sequence, Time to Live and Round Trip Time for each recieved ping. By pressing CTRL and C for a keyboard interrupt, there will be a print out of Ping Statistics for the packets transmitted and recieved before exiting the program. This will be printing out the packets transmitted, packets recieved, packet loss %, min time for the RTT, max time for the RTT and the average time for RTT from packets. The outputs were trying to match the formatted outputs of a normal ping program like that of "ping google.com" if typed into the command terminal.


