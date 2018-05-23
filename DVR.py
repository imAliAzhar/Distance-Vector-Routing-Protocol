from socket import *
from copy import deepcopy
import sys
import time
import threading
import json
import os
import math

from readFile import *

timeoutValue = 3
broadcastTime = 1

tableUpdateLock = threading.Lock()
broadcastLock = threading.Lock()

class Node():

    def __init__(self, name, port, neighbours):
        self.name = name
        self.port = int(port)
        self.neighbours = neighbours
        self.routingTable = {}
        self.routingTable[name] = {'through' : name, 'cost': 0, 'timeout' : math.inf}
        self.queue = []
        for node in neighbours:
            self.routingTable[node] = {'through' : node, 'cost': neighbours[node]['cost'], 'timeout' : time.time() + timeoutValue}
       


    def updateRoutingTable(self, DV, sendingNode):
        with tableUpdateLock:
            if sendingNode in self.routingTable:
                self.routingTable[sendingNode]['timeout'] = time.time() + timeoutValue
            for node in self.routingTable:
                if self.routingTable[self.routingTable[node]['through']]['cost'] == math.inf:
                    self.routingTable[node]['through'] = self.name
                    self.routingTable[node]['cost'] = math.inf
            for node in DV:
                if node not in self.routingTable or ( DV[node]['cost'] + self.neighbours[sendingNode]['cost'] < self.routingTable[node]['cost'] ):
                    self.routingTable[node] = {'through' : sendingNode, 'cost' : DV[node]['cost'] + self.neighbours[sendingNode]['cost'], 'timeout' : time.time() + timeoutValue}
                elif sendingNode == self.routingTable[node]['through'] and self.routingTable[node]['cost'] != self.routingTable[sendingNode]['cost'] + DV[node]['cost']:
                    self.routingTable[node]['cost'] = self.routingTable[sendingNode]['cost'] + DV[node]['cost']
            for node in DV:
                if self.routingTable[node]['through'] == sendingNode and DV[node] == math.inf:
                    self.routingTable[node]['through'] = self.name
                    self.routingTable[node]['cost'] = math.inf



    def broadcast(self):
        with broadcastLock:
            while True:
                self.display()
                sock = socket(AF_INET, SOCK_DGRAM)
                for neighbour_node in self.neighbours:
                    data = deepcopy(self.routingTable)
                    for node in data:
                        if node != self.name and node != neighbour_node:
                            if data[node]['through'] == neighbour_node:
                                data[node]['cost'] = math.inf
                    data['packettype'] = "DV"
                    data['sendingNode'] = self.name                
                    data = json.dumps(data)
                    sock.sendto(data.encode(), ('localhost',  self.neighbours[neighbour_node]['port']))
                time.sleep(broadcastTime)



    def listen(self):
        while True:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.bind(('localhost', self.port))
            data = sock.recv(2048).decode()
            data = json.loads(data)
            self.queue.append(data)



    def processQueue(self):
        while True:
            if len(self.queue) != 0:
                self.processPacket(self.queue[0])
                del(self.queue[0])



    def processPacket(self, data):
        packetType = data['packettype']
        del(data['packettype'])
        sendingNode = data['sendingNode']
        del data['sendingNode']
        if packetType == "DV":
            self.updateRoutingTable(data, sendingNode)
        elif(packetType == "change"):
            self.change(data)
    


    def killDeadNodes(self):
        while True:
            with tableUpdateLock:
                for node in self.neighbours:
                    if self.routingTable[node]['timeout'] < time.time():
                        self.routingTable[node]['cost'] = math.inf        
                        self.neighbours[node]['cost'] = math.inf


    def run(self):       
        listenThread = threading.Thread(target=self.listen)
        broadcastThread = threading.Thread(target=self.broadcast)
        processThread = threading.Thread(target=self.processQueue)
        killDeadNodesThread = threading.Thread(target=self.killDeadNodes)
        listenThread.start()
        broadcastThread.start()
        processThread.start()
        killDeadNodesThread.start()
        listenThread.join()
        broadcastThread.join()
        processThread.join()
        killDeadNodesThread.join()



    def display(self):
        with tableUpdateLock:
            os.system("cls")
            print("="*56)
            print("\n I am Router " + self.name + '\n')
            for node in self.routingTable:
                if self.routingTable[node]['cost'] != math.inf and node != self.name:
                    print(" Least cost path to router " + node + " : through " +  self.routingTable[node]['through'] + " with  cost " +  str("{0:.1f}".format(self.routingTable[node]['cost']) + "\n"))
            print("="*56)
    


    def displayPacket(self, packet, sendingNode):
        print("\nProcessing packet from ", sendingNode)
        for x in packet:
            print(x + " through " + packet[x]['through'] + " cost ", packet[x]["cost"])
            print()
    


    def change(self, message):
        self.neighbours[message['node']]['cost'] = float(message['cost'])
        self.routingTable[message['node']]['cost'] = float(message['cost'])
        print(message['node'] + " set to ", self.neighbours[message['node']]['cost'])



if __name__ == '__main__':
    node = Node(sys.argv[1], sys.argv[2], readFile(sys.argv[3]))
    node.run()
    input()