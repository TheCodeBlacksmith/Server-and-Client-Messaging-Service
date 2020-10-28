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

# dictionary for all clients' information
clients = {}
usernames = []

def broadcast(message, username = None):
    """
    broadcast a message to all other active clients 
    NOTE: the message should must be encoded in FORMAT before it broadcast is called!!!
    """
    for client in clients:
        client.send(message)
 

def receive_connections():
    while True:
        # Accept Connection
        connectionSocket, clientAddr = serverSocket.accept()

        # Request And Store username
        connectionSocket.send('!NICK!'.encode(FORMAT))
        username = connectionSocket.recv(1024).decode(FORMAT)

        if username not in usernames:
            connectionSocket.send('!GD_USR!'.encode(FORMAT))
            usernames.append(username)
            clients[connectionSocket] = {'username': username, 'msg': 'null', 'hashtags': 'null', 'operation': 'init'}
            
            print(MSG_CONNECT_ALERT)
            print(clients[connectionSocket])
            print(f"...for connection: {connectionSocket}")

            # Start Handling Thread For Client
            currThread = threading.Thread(target=handler, args=(connectionSocket, clientAddr)) # defines the handler as the method to deal with the connection
            currThread.start()
        else:
            connectionSocket.send('!ERR_USR!'.encode(FORMAT))    

def handler(client_connection_socket: socket, clientAddr):
    '''
    Desc: Maintains each client thread as it arrives to the server until termination. Based on the
    header information when reading the input form the client, the handler determines whether to
    upload or download a message and do subsequent actions inlcuding termination of the client upon
    completion of its task. 

    Parameters: client_connection_socket = client port, clientAddr = client address
    
    Note: the packet is a combination of the option designated the type of action
    (defined as "header") followed by the actual data
    '''

    # num = threading.activeCount() - 1

    while True:
        try:
            # message = client_connection_socket.recv(1024).decode(FORMAT)
            username, cmd, message, hashtags= [str(i) for i in client_connection_socket.recv(2048).decode(FORMAT).split('\n')]
            
            # prepare and print out server description of action
            if cmd == "tweet":
                    hashtags = hashtags.replace(" ", "")
                    hashtags_ls = list(set([str(tag) for tag in hashtags.split("#")]))
                    print(f"server read: TweetMessage {{username='{username}', msg='{message}', hashTags='{hashtags}', operation='{cmd}'}}")
                    to_send_message = f"{username}: {message} {hashtags.strip()}"
                    broadcast(to_send_message.encode(FORMAT))
                    print("finished")
            
            elif cmd == "subscribe":
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "unsubscribe":
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "gettweets":
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "timeline":
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "getusers":
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "exit":
                client_info = clients.pop(client_connection_socket)
                client_connection_socket.close

                usernames.pop(usernames.index(client_info["username"]))
                #print(f"thread active:  {threading.activeCount() - 1}, number os users: {len(usernames)}")
                broadcast(f'{client_info["username"]} left the chat!'.encode(FORMAT))
                break
            
        except:
            client_info = clients.pop(client_connection_socket)
            client_connection_socket.close

            usernames.pop(usernames.index(client_info["username"]))
            #print(f"thread active:  {threading.activeCount() - 1}, number os users: {len(usernames)}")
            broadcast(f'{client_info["username"]} left the chat!'.encode(FORMAT))
            break
       
    print( MSG_DISCONNECT_ALERT, clientAddr )

def start_server(PORT):
    '''
    Desc: Initializes server.
    
    Parameters: PORT = server port

    Note: the packet is a combination of the option designated the type of action
    (defined as "header") followed by the actual data
    '''
    serverSocket.listen()
    print (MSG_SRV_CONNECT_ALERT, PORT)
    
    while True:
        # try:
        receive_connections()   
        # except:
        # print (ERR_CLIENT_START, clientAddr)
 

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
# try:
PORT = arguments["ServerPort"]
serverSocket.bind((SERVER, PORT)) 
start_server(PORT)
# except:
#     print (ERR_SERVER_START, SERVER)
#     exit(0)


exit(0) #NOTE: redundant, location never reached
