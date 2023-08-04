from socket import * 
import threading
import sys
import argparse

FORMAT = 'utf-8'
MAX_DATA_SIZE = 150
FILENAME = "Sample.txt"

MSG_CLIENT_CONNECT = "username legal, connection established."
MSG_HASHTAG_OPERATION = "operation success"
MSG_CLIENT_TERMINATE = "bye bye"

ERR_SERVER_IP_INVALID = "error: server ip invalid, connection refused."
ERR_SERVER_PORT_INVALID = "error: server port invalid, connection refused."

ERR_USERNAME_INVALID = "error: username has wrong format, connection refused."
ERR_USERNAME_ILLEGAL = "username illegal, connection refused."

ERR_PARAMETERS = "error: args should contain <ServerIP>   <ServerPort> <Username>"

ERR_MSG_LENGTH_EXCEED = "message length illegal, connection refused."
ERR_MSG_LENGTH_ILLEGAL = "message format illegal."

ERR_HASHTAG_ILLEGAL = "hashtag illegal format, connection refused."
# NOTE: Maximum hashtags reached: “operation failed: sub <hashtag> failed, already exists or exceeds 3 limitation” must be implemented in code


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
        except Exception:
            
                
                if SERVER != "127.0.0.1":
                    print(ERR_SERVER_IP_INVALID) 
                elif PORT <= 80 or PORT > 65535:
                    print(ERR_SERVER_PORT_INVALID)
                else:
                    connectRes = self.clientSocket.connect_ex(("127.0.0.1", 13000))
                    if connectRes != 0:
                        print("connection error, please check your server: Connection refused")
                    else:
                        print(ERR_SERVER_PORT_INVALID)
                    self.clientSocket.close()
                 
        

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
if arguments["u"] and len(bytes(arguments["MSG"], FORMAT)) > MAX_DATA_SIZE: 
    size = len(bytes(arguments["MSG"]).encode(FORMAT))
    
    print (ERR_MSG_LENGTH_EXCEED, str(size))
    writeToFile(ERR_MSG_LENGTH_EXCEED + "" + str(size))
    
    print (MSG_CLIENT_TERMINATE)
    writeToFile(MSG_CLIENT_TERMINATE)
    
    exit(0)
else:
    if arguments["u"]: #CASE: upload case is selected
        client = Client(arguments["ServerIP"],arguments["ServerPort"], "u", arguments["MSG"] )
    elif arguments["d"]: #CASE: download case is selected
        client = Client(arguments["ServerIP"],arguments["ServerPort"], "d" )
    else: #CASE: (redundancy) if neither case is selected and program arrives here
        print (ERR_PARAMETERS)
        writeToFile(ERR_PARAMETERS)
        
        print (MSG_CLIENT_TERMINATE)
        writeToFile(MSG_CLIENT_TERMINATE)
        
        exit(0)



