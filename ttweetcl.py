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

MSG_CLIENT_CONNECT = "username legal, connection established."
MSG_HASHTAG_OPERATION = "operation success"
MSG_CLIENT_TERMINATE = "bye bye"

ERR_SERVER_IP_INVALID = "error: server ip invalid, connection refused."
ERR_SERVER_PORT_INVALID = "error: server port invalid, connection refused."
ERR_SERVER_NO_CONNECTION = "connection error, please check your server: Connection refused"

ERR_USERNAME_INVALID = "error: username has wrong format, connection refused."
ERR_USERNAME_ILLEGAL = "username illegal, connection refused."

ERR_PARAMETERS = "error: args should contain <ServerIP> <ServerPort> <Username>"

ERR_MSG_LENGTH_EXCEED = "message length illegal, connection refused."
ERR_MSG_FORMAT_ILLEGAL = "message format illegal."

ERR_HASHTAG_ILLEGAL = "hashtag illegal format, connection refused."
# NOTE: Maximum hashtags reached: “operation failed: sub <hashtag> failed, already exists or exceeds 3 limitation” must be implemented in code

class Client(object):
    timeline_of_all_messages = []
    clientSocket = socket(AF_INET, SOCK_STREAM) # defines usage of IPv4 and TCP connection is being used
    def data_validation(self, message = "", hashtags = [], version = 0, cmd = "Null"):
        """
        validates all parts of the data (message and/or hashtags)

        Parameters:
        - message = any message that has to be sent
        - hashtags = any hashtags that have to be sent
        - version = type of check (depnding on whether hashtasg and message is being sent or just one of them)
        NOTE: (0 == message AND hastags being sent, 1 == only message being sent, 2 == only hashtags being sent)
        - cmd = the command being executed

        """
        ## Validation of hashtags
        if version == 0 or version == 2:
            hashtags_ls = hashtags.split("#")
            hashtags_ls.pop(0) # NOTE: this pops of the extra "" whenever ther is a splitting of the #'s
            print(f"checking hashtags = {hashtags_ls}")
            # NOTE: limitation of 5 on the number of hashtag units for each data sent for tweet command
            if (len(hashtags_ls) > 5 or len(hashtags_ls) == 0) and cmd.strip() == "tweet":
                print("waa 1")
                print(ERR_MSG_FORMAT_ILLEGAL)
                return False
            # NOTE: limitation of 1 on the number of hashtag units for each data sent for subscribe and unsubscribe commands
            if len(hashtags_ls) > 1 and (cmd.strip() == "subscribe" or cmd.strip() == "unsubscribe"):
                print("waa 2")
                print(ERR_MSG_FORMAT_ILLEGAL)
                return False
            #  check if any empty violate hashtags format (hastags cannot be "" or non-alphanumeric or greater in length then 15 (# is already removed))
            if any(hashtag == "" or not (str(hashtag).isalpha() or str(hashtag).isalnum() or str(hashtag).isnumeric()) or len(hashtag) > 14 for hashtag in hashtags_ls):
                
                print(ERR_HASHTAG_ILLEGAL)
                return False
        
        ## Validation of message
        if version == 0 or version == 1:
            if message == "":
                print("waa 3")
                print(ERR_MSG_FORMAT_ILLEGAL)
                return False
            if len(message) > 150:
                print(ERR_MSG_LENGTH_EXCEED)
                return False

        return True


    # Listening to Server and Sending Username
    def receive(self):
        """
        receives any messages from the server

        TODO: delete unnesscary username validation code as it is implemented later below

        """
        print(f"receive start and threads are: {threading.activeCount()}")
        while True and threading.activeCount() >= 2:
            try:
                # Receive Message From Server
                # If '!NICK!' Send Username
                message = self.clientSocket.recv(2048).decode(FORMAT)
                if message == '!NICK!':
                    self.clientSocket.send(self.username.encode(FORMAT))
                elif message == '!ERR_USR!':
                    print(ERR_USERNAME_ILLEGAL)
                    self.clientSocket.close()
                    exit(0)
                    break
                else:
                    self.timeline_of_all_messages.append(message)
                    print(message)
            except Exception:
                # Close Connection When Error
                # print("An error occured!")
                self.clientSocket.close()
                break

    # Sending Messages To Server
    def write(self):
        """
        sends any messages to the server
        """
        cmd = ""
        message = ""
        print(f"write start and threads are: {threading.activeCount()}")
        while True and threading.activeCount() >= 2:
            try:
                full_msg = input(f'user {self.username} stdin command: ')
                
                ls = full_msg.split(" ", 1)
                if len(ls) > 1:
                    cmd, data = ls[0], ls[1]
                    print(f"cmd = {cmd}, data = {data}")
                    cmd = cmd.strip()
                    data = data.strip()
                    
                    # CASE: tweet COMMAND
                    if cmd == "tweet":
                        ls = data.split('"')
                        print(f"ls = {ls}")
                        if len(ls) != 3: # NOTE: should be ['', 'hello', ' #yo'] for ex.
                            print("waa 4")
                            print(ERR_MSG_FORMAT_ILLEGAL)
                            continue
                        message = ls[1]
                        hashtags = ls[2] #NOTE: hashtags will be split on the server side 
                        hashtags = hashtags.strip()
                        # if validation of data fails return to checing for new input
                        if not self.data_validation(message, hashtags, 0, cmd.strip()):
                            continue

                        print(f"SUCCESS: cmd = {cmd}, message = {message}, hashtags = {hashtags}")
                        self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))

                    elif cmd == "subscribe":
                        pass
                    elif cmd == "unsubscribe":
                        pass
                    elif cmd == "gettweets":
                        pass
                    else:
                        print("waa 5")
                        print(ERR_MSG_FORMAT_ILLEGAL)
                        continue                    
                else:
                    if full_msg.strip() == "timeline":
                        pass
                    elif full_msg.strip() == "getusers":
                        pass
                    
                    # CASE: exit COMMAND
                    elif full_msg.strip() == 'exit':
                        cmd = "exit"
                        message = "None"
                        # self.clientSocket.send([self.username, cmd, message].encode(FORMAT))
                        self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message]), FORMAT)) 
                        print(MSG_CLIENT_TERMINATE)
                        self.clientSocket.close() 
                        break
                    # CASE: no valid command passed
                    else:
                        print("waa 6")
                        print(ERR_MSG_FORMAT_ILLEGAL)
                        continue

            except Exception:
                 self.clientSocket.close()
                 break         

    def __init__(self, SERVER, PORT, username):
        '''
        Desc: Method initializes client or else will ecxecute the appropriate command
        
        Parameters: 
        - SERVER = server ip
        - PORT = server port,
        - text = (default is "") holds username, or the 150 char message, hashtag depending on the  command parameter
        - command (default is None) (parameter holds the type of command the client wants to execute (None for logging in))
        '''
        self.username = username
        # CASE: new client is trying to log in
        try:
            print(f"got username = {self.username}")
            self.clientSocket.connect((SERVER, PORT))
            
            message = self.clientSocket.recv(1024).decode(FORMAT)
            # CASE: Server is asking for username after getting connection
            if message == '!NICK!':
                self.clientSocket.send(self.username.encode(FORMAT))
                
            message = self.clientSocket.recv(1024).decode(FORMAT)
            # CASE: Server rejects username due to it already existing
            if message == '!ERR_USR!':
                print(ERR_USERNAME_ILLEGAL)
                self.clientSocket.close()
                exit(0)
            # CASE: Server accepts username
            elif message == "!GD_USR!":
                print(f"before any start and threads are: {threading.activeCount()}")
                # Starting Threads For Listening And Writing
                receive_thread = threading.Thread(target=self.receive)
                receive_thread.start()
                
                write_thread = threading.Thread(target=self.write)
                write_thread.start()
            else:
                
                exit(0)

            
            
            
            
            #self.clientSocket.close()
            #print ("Transmission Successfull...")
            
            #exit(0)
        except Exception:
            # Exception handles invalid SERVER and/or PORT
            if SERVER != "127.0.0.1":
                print(ERR_SERVER_IP_INVALID) 
            elif PORT <= 80 or PORT > 65535:
                print(ERR_SERVER_PORT_INVALID)
            else:
                connectRes = self.clientSocket.connect_ex(("127.0.0.1", 13000))
                if connectRes != 0:
                    print(ERR_SERVER_NO_CONNECTION)
                else:
                    print(ERR_SERVER_PORT_INVALID)
                self.clientSocket.close()
        
        # CASE: tweet command being launched
        
                 
        

'''
--------------------------------------------------------------------------------------------------------
Command line interface implementation & processing
--------------------------------------------------------------------------------------------------------
'''
parser = argparse.ArgumentParser(description='Optional app description')

parser.add_argument('ServerIP', action='store', type=str, help='Server IP address') # Required
parser.add_argument('ServerPort', action='store', type=int, help='Server Port address') # Required
parser.add_argument('Username', action='store', type=str, help='Username (alphanumeric)') # Required

# check if the parameters are the correct amount
num_of_arguments = len(sys.argv) - 1
if num_of_arguments != 3:
    print(ERR_PARAMETERS)
    exit(0)

# parse arguments to make sure they are valid
arguments = vars(parser.parse_args())

'''
--------------------------------------------------------------------------------------------------------
Username validation logic and client logging in logic
--------------------------------------------------------------------------------------------------------
'''

# check username is not "" or non-alphanumeric
if len(arguments["Username"]) == 0 or not str(arguments["Username"]).isalnum() or len(arguments["Username"]) > 150:
    print(ERR_USERNAME_INVALID)
    exit(0)

# try logging in the user
client = Client(arguments["ServerIP"], arguments["ServerPort"], arguments["Username"] ) 
exit(0)




