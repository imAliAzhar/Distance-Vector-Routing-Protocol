import sys
import time
import os
import msvcrt
from socket import *
import json
import threading

from readFile import *



sendlock = threading.Lock()
def send(port, node, cost):
    #sends packet to the node whose distance has changed
    with sendlock:
        sock = socket(AF_INET, SOCK_DGRAM)
        message = {}
        message['packettype'] = "change"
        message['sendingNode'] = "CostEditor"
        message['node'] = node
        message['cost'] = cost
        message['port'] = port
        message = json.dumps(message)
        sock.sendto(message.encode(), ('localhost',  port))




#reads the original distances between the nodes
#nodes: stores the read files data
nodes = {}
for x in range (1, len(sys.argv)):
    node = sys.argv[x][-5]
    nodes[node] = readFile(sys.argv[x])



#pointer: keep tracks of the arrow which points to the current highlighted option
#userInput: stores input from the keyboard; 'n' means no input
#nodestaken: used as a flag when nodes to be changed hace been selected
pointer = 0
userInput = 'n'
nodestaken = False



while True:
    os.system("cls")
    print("\n\t         COST EDITOR\n")
    print("\t   Use Q and W for cursor\n\t   Use double E to select\n\n")
    print("="*44)
    #done: stores the nodes that have been printed; 
    #makes sure same distances are not repeated that
    # is after 'A and B', no 'B and A' is printed
    done = []
    optionNum = 0
    for nodeA in nodes:
        for nodeB in nodes[nodeA]:
            if nodeB not in done:
               if(optionNum == pointer):
                   print("  ->", end="")
                   if(userInput == 'E' or userInput == 'e'):
                        nodestaken = True
                        nodeAChanged = nodeA
                        nodeBChanged = nodeB
                        userInput = 'n'
               print("\t Cost between " + nodeA + " and " + nodeB + " is " + str("{0:.1f}".format(float(nodes[nodeA][nodeB]['cost']))).strip('{}'))
               optionNum += 1
        done.append(nodeA)
    print("="*44)
    #get input from the user
    userInput = msvcrt.getch().decode("utf-8")
    if (userInput == 'Q' or userInput == 'q'):
        pointer -= 1
    elif (userInput == 'W' or userInput == 'w'):
        pointer += 1
    #keeps the pointer in range 0 to optionNum
    if(pointer < 0):
        pointer = 0
    if(pointer > optionNum - 1):
        pointer = optionNum - 1
    #if nodes have been selected
    if(nodestaken):
        nodestaken = False
        userInput = 'n'
        print("\n    Enter new cost for nodes " + nodeAChanged + " and " + nodeBChanged + " : ", end="")
        newcost = input()
        print()
        #send packet to first node
        print("  Sending control packet to " + nodeAChanged + " at port" , nodes[nodeBChanged][nodeAChanged]['port'])
        changethread1 = threading.Thread(target=send,  kwargs={'port': nodes[nodeBChanged][nodeAChanged]['port'], 'node' : nodeBChanged, 'cost' : newcost})
        changethread1.start()
        #send packet to second node
        print("  Sending control packet to " + nodeBChanged + " at port" , nodes[nodeAChanged][nodeBChanged]['port'])
        changethread2 = threading.Thread(target=send,  kwargs={'port': nodes[nodeAChanged][nodeBChanged]['port'], 'node' : nodeAChanged, 'cost' : newcost})
        changethread2.start()
        #update the costs here as well
        nodes[nodeAChanged][nodeBChanged]['cost'] = newcost
        nodes[nodeBChanged][nodeAChanged]['cost'] = newcost
        time.sleep(1)
        print("\n              Costs updated")
        time.sleep(2)