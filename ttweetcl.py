'''
 *
 * Citations: 
 *  - Used TCPClient.py code from Computer Networking Textbook (pg: 205) as a reference
 *  - https://realpython.com/python-command-line-arguments/#subcommands 
 *  - https://stackabuse.com/command-line-arguments-in-python/
 *
'''

from socket import * 
import threading
import sys
import argparse

FORMAT = 'utf-8'
MAX_DATA_SIZE = 150
FILENAME = "Sample.txt"
#SERVER = gethostbyname(gethostname()) # gets the host IP of current computer
#SERVER = "127.0.0.1"

MSG_CLIENT_TERMINATE = "CLIENT ALERT: [GENERAL] Client Terminated"

ERR_LENGTH_EXCEED = "CLIENT ALERT: [ERROR] Max of 150 characters for message surpassed. Actual size given (bytes): "
ERR_SERVER_CONNECT = "CLIENT ALERT: [ERROR] Server is not available for TTweet. Please connect to 127.0.0.1 when server is online."
ERR_GENERAL = "CLIENT ALERT: [ERROR] Parameters are invalid"


def writeToFile(data):
    '''
    Desc: Helper method to write to the sample file all text output
    '''
    with open(FILENAME, 'a') as f:
        data += '\n'
        f.write(data)

class Client(object):
    clientSocket = socket(AF_INET, SOCK_STREAM) # defines usage of IPv4 and TCP connection is being used
    
    def send_data(self, data):
        '''
        Desc: Sends the data to the server

        Parameters: data = data to be sent to server
        
        Note: the packet is a combination of the option designated the type of action
        (defined as "header") followed by the actual data
        '''
        header = "u" # signifies to server that upload is being done
        self.clientSocket.sendall(str.encode("\n".join([header, data]), FORMAT))


    def receive_data(self):
        '''
        Desc: Gets the last sent message from the server
        '''
        header = "d" # signifies to server that download is being done
        data = ""
        self.clientSocket.sendall(str.encode("\n".join([header, data]), FORMAT))
        received_msg = self.clientSocket.recv(1048).decode(FORMAT)
        
        print ("Received Message: ",received_msg) 
        writeToFile("Received Message: " + received_msg)

    def __init__(self, SERVER, PORT, option, message = ""):
        '''
        Desc: Method initializes client and determines action to take.
        Each call is placed into a thread which will either upload or 
        downlaod a message and then terminate. 
        
        Parameters: SERVER = server ip, PORT = server port, option = defines if your going to upload or download
        message = (default is "") holds the 150 char message
        '''
        try:
            self.clientSocket.connect((SERVER, PORT))

            if option == "u": # Upload option
                input_thread = threading.Thread(target=self.send_data(message))

            elif option == "d": # Download option
                input_thread = threading.Thread(target=self.receive_data())

            self.clientSocket.close()
            print ("Transmission Successfull...")
            writeToFile("Transmission Successfull...")
            exit(0)
            print("done")
        except Exception: #NOTE: Python 3 : just--> except: DONE
            print (ERR_SERVER_CONNECT)
        

'''
--------------------------------------------------------------------------------------------------------
Command line interface implementation & processing
--------------------------------------------------------------------------------------------------------
'''
parser = argparse.ArgumentParser(description='Optional app description')

cmd_group = parser.add_mutually_exclusive_group(required=True)

cmd_group.add_argument('-u', action='store_true', help="option for uploading message")
cmd_group.add_argument('-d', action='store_true', help="option for downloading message")

parser.add_argument('ServerIP', action='store', type=str, help='Server IP address') # Required
parser.add_argument('ServerPort', action='store', type=int, help='Server Port address') # Required
if '-u' in sys.argv:
    parser.add_argument('MSG', action='store', type=str, help='client message')

#parse arguments to make sure they are valid
arguments = vars(parser.parse_args())

'''
--------------------------------------------------------------------------------------------------------
UPLOAD MODE and DOWNLOAD MODE logic
--------------------------------------------------------------------------------------------------------
'''
#NOTE: Python 3 : just--> if arguments["u"] and len(bytes(arguments["MSG"], FORMAT)) > MAX_DATA_SIZE: # DONE
if arguments["u"] and len(bytes(arguments["MSG"], FORMAT)) > MAX_DATA_SIZE: 
    size = len(bytes(arguments["MSG"]).encode(FORMAT))
    
    print (ERR_LENGTH_EXCEED, str(size))
    writeToFile(ERR_LENGTH_EXCEED + "" + str(size))
    
    print (MSG_CLIENT_TERMINATE)
    writeToFile(MSG_CLIENT_TERMINATE)
    
    exit(0)
else:
    if arguments["u"]: #CASE: upload case is selected
        client = Client(arguments["ServerIP"],arguments["ServerPort"], "u", arguments["MSG"] )
    elif arguments["d"]: #CASE: download case is selected
        client = Client(arguments["ServerIP"],arguments["ServerPort"], "d" )
    else: #CASE: (redundancy) if neither case is selected and program arrives here
        print (ERR_GENERAL)
        writeToFile(ERR_GENERAL)
        
        print (MSG_CLIENT_TERMINATE)
        writeToFile(MSG_CLIENT_TERMINATE)
        
        exit(0)



