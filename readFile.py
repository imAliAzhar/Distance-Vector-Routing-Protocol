def readFile(filename):
    filename = "C:\\" + filename
    IN_FILE = open(filename, 'r')
    NEIGHBORS = {}
    COUNTER = 0
    for line in IN_FILE:
        if COUNTER == 0:
            noOfNeighbors = int(line)
            COUNTER = COUNTER + 1
        else:
            words = line.split(" ")
            neighbor = words[0]
            weight = float(words[1])
            port = int(words[2])
            NEIGHBORS[neighbor] = {'cost': weight, 'port': port}
    return NEIGHBORS