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
import time
import select

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
    lock = threading.Lock()
    timeline_of_all_messages = []
    subscribed_hashtags = []
    clientSocket = socket(AF_INET, SOCK_STREAM) # defines usage of IPv4 and TCP connection is being used
    lock_for = "write"
    def data_validation(self, message = "", hashtags = "", version = 0, cmd = "Null"):
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
            
            # NOTE: limitation of 5 on the number of hashtag units for each data sent for tweet command
            if (len(hashtags_ls) > 5 or len(hashtags_ls) == 0) and cmd.strip() == "tweet":
                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                return False
            
            # NOTE: limitation of 1 on the number of hashtag units for each data sent for subscribe and unsubscribe commands
            if len(hashtags_ls) != 1 and (cmd.strip() == "subscribe" or cmd.strip() == "unsubscribe"):
                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                return False

            if (any(hashtag in self.subscribed_hashtags for hashtag in hashtags_ls) and cmd.strip() == "subscribe") or (len(self.subscribed_hashtags) >= 3 and cmd.strip() == "subscribe"):
                print(f"operation failed: sub {hashtags.strip()} failed, already exists or exceeds 3 limitation " + "\n")
                return False
            
            # NOTE: for unsubscribe, nothing needs to happen if the hashtag is not subscribed to
            if hashtags_ls[0] != 'ALL' and (not any(hashtag in self.subscribed_hashtags for hashtag in hashtags_ls) and cmd.strip() == "unsubscribe"):
                return False

            # NOTE: for unsubscribe, nothing needs to happen if the no hashtyags is  subscribed to and #ALL is invoked
            if hashtags_ls[0] == 'ALL' and len(self.subscribed_hashtags) == 0 and cmd.strip() == "unsubscribe":
                return False

            if any(hashtag == "ALL" for hashtag in hashtags_ls) and cmd.strip() == "tweet":
                # NOTE: while ' or hashtag == "ALL" ' will not be tested, it is not allowed according to instructions for tweet
                print(ERR_HASHTAG_ILLEGAL + "\n")
                return False

            #  check if any empty violate hashtags format (hastags cannot be "" or non-alphanumeric or greater in length then 15 (# is already removed))
            if any(hashtag == ""  or not (str(hashtag).isalpha() or str(hashtag).isalnum() or str(hashtag).isnumeric()) or len(hashtag) >= 15 for hashtag in hashtags_ls):
                print(ERR_HASHTAG_ILLEGAL + "\n")
                return False
        
        ## Validation of message
        if version == 0 or version == 1:
            if message == "":
                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                return False
            if len(message) > 150:
                print(ERR_MSG_LENGTH_EXCEED + "\n")
                return False

        return True


    # Listening to Server and Sending Username
    def receive(self):
        """
        receives any messages from the server

        TODO: delete unnesscary username validation code as it is implemented later below

        """
        
        while True:
            try:
                # Receive Message From Server
                # If '!NICK!' Send Username
                message = self.clientSocket.recv(2048).decode(FORMAT)
                if message == '!NICK!':
                    self.clientSocket.send(self.username.encode(FORMAT))
                elif message == '!ERR_USR!':
                    print(ERR_USERNAME_ILLEGAL + "\n")
                    self.clientSocket.close()
                    exit(0)
                    break
                elif '!E_TWT_USR!' in  message:
                    with self.lock:
                        print(message.replace('!E_TWT_USR!', ""))
                        self.lock_for = "write"
                else:
                    if message[-3:] == '###': #CASE: getusers info requested divert message to special variable
                        with self.lock:
                            print(message.replace('###', ''))
                            self.lock_for = "write"
                    else:
                        if '##!NO_MSG!##' not in message:
                            cus_message = message
                            cus_message += '\n'
                            
                            if message.find(self.username) != 0:
                                cus_message = '\n' + cus_message + f'\nuser {self.username} stdin command: '
                            
                            self.lock_for = "read"
                            with self.lock:
                                if message.find(self.username) != 0:
                                    print(cus_message, end = "")
                                else:
                                    print(cus_message)
                                self.timeline_of_all_messages.append(message)
                                self.lock_for = "write"
                            #-------or---------------------------------
                            # if self.lock_for == "read":
                            #     with self.lock:
                            #         print("case 1", end = " ")
                            #         print(message, end = " ")
                            #         self.timeline_of_all_messages.append(message)
                            #         self.lock_for = "write"
                            # else: # CASE: valid input received but not in lock
                            #     print("case 2", end= " ")
                            #     print(message, end = " ")
                            #     self.lock_for = "write"
                            #-------or---------------------------------
                        else: # CASE: no valid input received
                            # print('##!NO_MSG!## ', end =" ")
                            # print("case 3" , end= " ")
                            self.lock_for = "write"
            except Exception:
                # Close Connection When Error
                self.clientSocket.close()
                break

    # Sending Messages To Server
    def write(self):
        """
        sends any messages to the server
        """
        cmd = ""
        message = ""
        
        while True:
            try:
                if self.lock_for != "read":
                    # with self.lock:
                    full_msg = input(f'user {self.username} stdin command: ')
                    ls = full_msg.split(" ", 1)
                    if len(ls) > 1:
                        cmd, data = ls[0], ls[1]
                        cmd = cmd.strip()
                        data = data.strip()
                        
                        # CASE: tweet COMMAND
                        if cmd == "tweet":
                            ls = data.split('"')
                            if len(ls) != 3: # NOTE: should be ['', 'hello', ' #yo'] for ex.
                                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                                continue
                            message = ls[1]
                            hashtags = ls[2] #NOTE: hashtags will be split on the server side 
                            hashtags = hashtags.strip()
                            # if validation of data fails return to checing for new input
                            if not self.data_validation(message, hashtags, 0, cmd.strip()):
                                continue

                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))
                            # print("") #skip line requirement
                            self.lock_for = "read"

                        elif cmd == "subscribe":
                            message = " "
                            hashtags = data
                            
                            if not self.data_validation(message, hashtags, 2, cmd.strip()):
                                continue

                            print(MSG_HASHTAG_OPERATION + "\n")
                            
                            hashtags_ls = hashtags.split('#')
                            self.subscribed_hashtags.append(hashtags_ls[1])
                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))

                        elif cmd == "unsubscribe":
                            message = " "
                            hashtags = data
                            
                            if not self.data_validation(message, hashtags, 2, cmd.strip()):
                                continue

                            print(MSG_HASHTAG_OPERATION + "\n") 
                            
                            hashtags_ls = hashtags.split('#')
                            if hashtags_ls[1] == 'ALL':
                                self.subscribed_hashtags = []
                            else:
                                self.subscribed_hashtags.remove(hashtags_ls[1])
                            
                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))

                        elif cmd == "gettweets":
                            message = data
                            hashtags = "None"

                            if not self.data_validation(message, hashtags, 1, cmd.strip()):
                                continue

                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))
                            self.lock_for = "read"

                        else:
                            if full_msg != "":
                                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                                continue
                            else:
                                continue                    
                    else:
                        if full_msg.strip() == "timeline":
                            for received_msg in self.timeline_of_all_messages:
                                print(received_msg)
                            print("") # skip a line based on formatting in instructions
                        
                        elif full_msg.strip() == "getusers":
                            cmd = "getusers"
                            message = "None"
                            hashtags = "None"
                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))
                            self.lock_for = "read"
                        
                        # CASE: exit COMMAND
                        elif full_msg.strip() == 'exit':
                            cmd = "exit"
                            message = "None"
                            hashtags = "None"
                            #self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message]), FORMAT)) 
                            self.clientSocket.sendall(str.encode("\n".join([self.username, cmd, message, hashtags]), FORMAT))

                            print(MSG_CLIENT_TERMINATE)
                            self.clientSocket.close() 
                            break
                        # CASE: no valid command passed
                        else:
                            if full_msg != "":
                                print(ERR_MSG_FORMAT_ILLEGAL + "\n")
                                continue
                            else:
                                continue  
            except Exception:
                print(MSG_CLIENT_TERMINATE)
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
            self.clientSocket.connect((SERVER, PORT))
            
            message = self.clientSocket.recv(1024).decode(FORMAT)
            # CASE: Server is asking for username after getting connection
            if message == '!NICK!':
                self.clientSocket.send(self.username.encode(FORMAT))
                
            message = self.clientSocket.recv(1024).decode(FORMAT)
            # CASE: Server rejects username due to it already existing
            if message == '!ERR_USR!':
                print(ERR_USERNAME_ILLEGAL + "\n")
                self.clientSocket.close()
                exit(0)
            # CASE: Server accepts username
            elif message == "!GD_USR!":
                print(MSG_CLIENT_CONNECT + "\n")
                
                # Starting Threads For Listening And Writing
                receive_thread = threading.Thread(target=self.receive)
                receive_thread.start()
                
                write_thread = threading.Thread(target=self.write)
                write_thread.start()
            else:
                
                exit(0)

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




