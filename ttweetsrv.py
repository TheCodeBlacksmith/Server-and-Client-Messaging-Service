from socket import * 
import threading
import sys
import argparse

FORMAT = 'utf-8'
MAX_DATA_SIZE = 150
FILENAME = "Sample.txt" # name for text output file
# SERVER = gethostbyname(gethostname()) # gets the host IP of current computer
SERVER = "127.0.0.1" # set to local host
LAST_MESSAGE = "Empty Message" # storage point of ast inputted message in server session

MSG_SRV_CONNECT_ALERT = "server listening at "
MSG_CONNECT_ALERT = "server get connection!"
# TODO: delete immedietlly below message ONLY once code is updated
MSG_DISCONNECT_ALERT = "SERVER ALERT [CONNECTION] DISCONNECTION OF CLIENT: "

# TODO: delete below message ONLY once message received statement is implemented in code 
# e.g: server read: TweetMessage{username='cxworks', msg='null', hashTags='null', operation='init'}
MSG_RECEIVED = "SERVER ALERT [GENERAL] Message Received: "

# TODO: implement in code server write message
# e.g: server write: TweetResponse{success=true, type='subscribe', error='null', tweetMsg='null', hashTags='null', sender='null', notification='null', usernames=0, historyMessages=0}
ERR_SERVER_START = "server could not start at "
# TODO: delete immedietlly below message ONLY once code is updated
ERR_CLIENT_START = "SERVER ALERT [ERROR] COULD NOT START CLIENT: "
# TODO: delete immedietlly below message ONLY once code is updated
ERR_CLIENT_INPUT = "SERVER ALERT [ERROR] INPUT COULD NOT BE PROCESSED FORM CLIENT: "


serverSocket = socket(AF_INET, SOCK_STREAM) # defines usage of IPv4 and TCP connection is being used

def printServerStats(parameter_list):
    """
    Desc: Helper method that prints the number of active clients
    """
    print(" Total clients: ",  threading.activeCount() - 1)

def clearFile():
    '''
    Desc: Helper method to clear text file on each server start
    '''
    file = open(FILENAME,"w")
    file.close()

def writeToFile(data):
    '''
    Desc: Helper method to write to the sample file all text output
    '''
    with open(FILENAME, 'a') as f:
        data += '\n'
        f.write(data)

def handler(connectionSocket, clientAddr):
    '''
    Desc: Maintains each client thread as it arrives to the server until termination. Based on the
    header information when reading the input form the client, the handler determines whether to
    upload or download a message and do subsequent actions inlcuding termination of the client upon
    completion of its task. 

    Parameters: connectionSocket = client port, clientAddr = client address
    
    Note: the packet is a combination of the option designated the type of action
    (defined as "header") followed by the actual data
    '''
    global MAX_DATA_SIZE
    global LAST_MESSAGE

    print(MSG_CONNECT_ALERT)
    num = threading.activeCount() - 1
    writeToFile(MSG_CONNECT_ALERT)

    connected = True
    while connected:
        try:
            header, data = [str(i) for i in connectionSocket.recv(2048).decode(FORMAT).split('\n')]
            #TEST: print(f"option: {header}, and data: {data}")
        except:
            if data == "":
                LAST_MESSAGE = "Empty Message"
                print(MSG_RECEIVED, data)
                writeToFile(MSG_RECEIVED + "" + "Empty Message")
                connected = False
                break
            else:
                print( ERR_CLIENT_INPUT, clientAddr )
                writeToFile(ERR_CLIENT_INPUT + "" + str(clientAddr))
                connected = False
                break

        if header == "u" and data:
            LAST_MESSAGE = data
            print( MSG_RECEIVED, data)
            writeToFile(MSG_RECEIVED + "" + data)
            connected = False

        elif header == "d":
            connectionSocket.sendall(str.encode(LAST_MESSAGE, FORMAT))
            connected = False

    if connected == False:
        print( MSG_DISCONNECT_ALERT, clientAddr )
        writeToFile(MSG_DISCONNECT_ALERT + "" + str(clientAddr))

def start_server(PORT):
    '''
    Desc: Initializes server. This also includes clearing text output file.
    
    Parameters: PORT = server port

    Note: the packet is a combination of the option designated the type of action
    (defined as "header") followed by the actual data
    '''
    clearFile() #NOTE: clear text output file each start of server
    serverSocket.listen() #NOTE: Python 3 : just--> serverSocket.listen() # DONE
    print (MSG_SRV_CONNECT_ALERT, PORT)
    writeToFile(MSG_SRV_CONNECT_ALERT + "" + PORT)
    
    while True: 
        try:   
            connectionSocket, clientAddr = serverSocket.accept()
        except:
            print (ERR_CLIENT_START, clientAddr)
            writeToFile(ERR_CLIENT_START + "" + str(clientAddr))
        currThread = threading.Thread(target=handler, args=(connectionSocket, clientAddr)) # defines the handler as the method to deal with the connection
        currThread.start()
 

'''
--------------------------------------------------------------------------------------------------------
Command line interface implementation & processing
--------------------------------------------------------------------------------------------------------
'''

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('ServerPort', action='store', type=int, help='Server Port address') # Required

#parse arguments to make sure they are valid
arguments = vars(parser.parse_args())


'''
--------------------------------------------------------------------------------------------------------
Server activation
--------------------------------------------------------------------------------------------------------
'''
try:
    PORT = arguments["ServerPort"]
    serverSocket.bind((SERVER, PORT)) 
    start_server(PORT)
except:
    print (ERR_SERVER_START, SERVER)
    writeToFile(ERR_SERVER_START + "" + SERVER)
    exit(0)


exit(0) #NOTE: redundant, location never reached
