from socket import *
import os
import sys
import struct
import time
import select
import binascii
import signal

ICMP_ECHO_REQUEST = 8
#adding in global variables
packets_transmitted=0
packets_recieved=0
packet_loss=0.0
min_rtt=999.0
max_rtt=0.0
return_time=[]


#signal handler
def keyboardInterruptHandle(signal, frame):
    global packets_recieved
    global packets_transmitted
    global packet_loss
    global min_rtt
    global max_rtt
    global return_time
    print()
    print("=====Ping Statistics=====")
    print("Packets Transmitted:", packets_transmitted)
    print("Packets Recieved:", packets_recieved)
    print("Packet Loss:", ((packet_loss/packets_transmitted)*100.0),"%")
    print("Round Trip Time...")
    print("Min time:", min_rtt," ms")
    print("Max time:", max_rtt," ms")
    print("Avg time:", (sum(return_time) / len(return_time) )," ms")
    exit(0);


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
        
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff
        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    ##get global values     global packets_recieved
    global packets_recieved
    global packet_loss
    global min_rtt
    global max_rtt
    global avg_rtt

    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        #print(whatReady[0])
        if whatReady[0] == []: # Timeout
            packet_loss+=1
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        #return recPacket
        


        packets_recieved+=1
        #Fetch the ICMP header from the IP packet
        
        #get information from header
        headerData=recPacket[20:28]
        icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_sequence = struct.unpack('bbHHh',headerData)
        
        #get the ttl
        icmp_ttl=recPacket[9:10] 
        
        #get the time sent data and store in time_sent
        time_package = struct.unpack('d',recPacket[28:28+8])
        time_sent=time_package[0]
        
        #get the min and max values and add into avg
        round_trip_time=(timeReceived-time_sent)*1000
        if round_trip_time<min_rtt:
            min_rtt=round_trip_time
        elif round_trip_time>max_rtt:
            max_rtt=round_trip_time
        return_time.append(round_trip_time)

        #print out values
        print("ICMP sequence=",icmp_sequence,"   TTL=",int.from_bytes(icmp_ttl, byteorder ='big'), "   Time=",((timeReceived-time_sent)*1000)," ms")

        return "Finished reading recieved packet..."


        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    global packets_transmitted
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    packets_transmitted+=1
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    

    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging host: " + host + " at: " + dest + " using Python:")
    print("")

    # Send ping requests to a server separated by approximately one second
    while 1 :
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)# one second
    return delay

if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboardInterruptHandle)
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    ping(host)