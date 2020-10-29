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
clients = {} #NOTE: each client has {'username': username, 'msg': [], 'hashTags': [], 'operation': 'init'} ('null' is default for any empty thing)
usernames = []


def update_hashTags(client, hashtags_added_ls, cmd=None):
    """
    helper method for updating a client's subscribed or unsubscribed hashtags
    NOTE: the method that calls this method should already check for if the client already has 3 hashtags
    """
    if cmd == None or cmd == "subscribe":
        curr_hashtags = clients[client]['hashTags']
        
        for tag in hashtags_added_ls:
            if tag not in curr_hashtags:
                curr_hashtags.append(tag)

        clients[client]['hashTags'] = list(set(curr_hashtags))

    elif cmd == "unsubscribe":
        curr_hashtags = clients[client]['hashTags']

        # CASE: if #ALL is the one to unsubscribe from
        if 'ALL' in hashtags_added_ls: 
            clients[client]['hashTags'] = curr_hashtags.clear() #wipe out all hashtags
        else:
        # CASE: remove the specific hashtag IF it exists (it should only be one hashtag)
            for hashtag in hashtags_added_ls:
                if hashtag in curr_hashtags:
                    curr_hashtags.remove(hashtag)

def broadcast(message, hashtags_ls = None, version = 0, username = None):
    """
    broadcast a message to all other active clients if they have the correct tags 
    NOTE: the message should must be encoded in FORMAT before broadcast() is called!!!
    """
    if version == 0:
        # print(f"hashtags list  = {hashtags_ls}") #TEST
        for client in clients:
            # print(f"client is: {clients[client]}") #TEST
            # if the #ALL is in the clients or has one of the tags sent by the tweeter, then send the tweet to them 
            if "ALL" in clients[client]['hashTags'] or any(e in hashtags_ls for e in clients[client]['hashTags']):
                # print(f"sending message: {str(message)} to: {clients[client]['username']}") #TEST
                client.send(message)
            # else:
            #     client.send("")
    
    #CASE: special braodcast situation called (getusers or gettweets)
    elif version == 1:
        getReceiving_client = next((client for client in clients if clients[client]['username'] == username))
        getReceiving_client.send(message)

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
            clients[connectionSocket] = {'username': username, 'msg': [], 'hashTags': [], 'operation': 'init'}
            
            #TEST
            # print(clients[connectionSocket])
            # print(f"...for connection: {connectionSocket}")
            print(MSG_CONNECT_ALERT)
            print(f"server read: TweetMessage{{ username='{username}', msg='null', hashTags='null', operation='init'}}")
            
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
            username, cmd, message, hashtags = input_vars  = [str(i) for i in client_connection_socket.recv(2048).decode(FORMAT).split('\n')]

            # prepare and print out server description of action
            if cmd == "tweet":
                hashtags = hashtags.replace(" ", "")
                hashtags_ls = list(set([str(tag) for tag in hashtags.split("#")]))
                hashtags_ls.pop(0) # NOTE: this pops of the extra "" whenever ther is a splitting of the #'s
                # print(f"hashtags_ls = {hashtags_ls}") #TEST

                print(f"server read: TweetMessage {{username='{username}', msg='{message}', hashTags='{hashtags}', operation='{cmd}'}}")

                to_send_message = f'{username}: "{message}" {hashtags.strip()}'

                #add the tweet to this client's history
                tweeting_client = next((client for client in clients if clients[client]['username'] == username))
                clients[tweeting_client]['msg'].append(to_send_message)

                broadcast(to_send_message.encode(FORMAT), hashtags_ls)
                # print("finished") #TEST
            
            elif cmd == "subscribe":
                hashtags = hashtags.replace(" ", "")
                hashtags_ls = list(set([str(tag) for tag in hashtags.split("#")]))
                hashtags_ls.pop(0) # NOTE: this pops of the extra "" whenever ther is a splitting of the #'s

                subscribing_client = next((client for client in clients if clients[client]['username'] == username))
                clients[subscribing_client]['hashTags'].append(hashtags_ls[0])
                print(f"server read: TweetMessage {{username='{username}', msg='null', hashTags='#{hashtags_ls[0]}', operation='{cmd}'}}")
            
            elif cmd == "unsubscribe":
                hashtags = hashtags.replace(" ", "")
                hashtags_ls = list(set([str(tag) for tag in hashtags.split("#")]))
                hashtags_ls.pop(0) # NOTE: this pops of the extra "" whenever ther is a splitting of the #'s

                subscribing_client = next((client for client in clients if clients[client]['username'] == username))
                curr_hashtags = []
                curr_hashtags = clients[subscribing_client]['hashTags']
                if hashtags_ls[0] == "ALL": #clear all hashtags if received hahstag is #ALL
                    clients[subscribing_client]['hashTags'] = []
                else:
                    clients[subscribing_client]['hashTags'].remove(hashtags_ls[0])
                print(f"server read: TweetMessage {{username='{username}', msg='null', hashTags='#{hashtags_ls[0]}', operation='{cmd}'}}")
            
                # print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "gettweets":
                tweetsOfUsername = message
                if tweetsOfUsername in usernames:
                    tweetsOf_client = next((client for client in clients if clients[client]['username'] == tweetsOfUsername))
                    tweets_List = clients[tweetsOf_client]['msg'] #gives the full list of all tweets sent by this user

                    getTweets_msg = "\n".join([str(tweet_msg) for tweet_msg in tweets_List]) + "\n"
                    to_send_message = f'{getTweets_msg} ###'

                    broadcast(to_send_message.encode(FORMAT), None, 1, username)
                else:
                    getReceiving_client = next((client for client in clients if clients[client]['username'] == username))
                    getReceiving_client.send(f'!E_TWT_USR!no user {tweetsOfUsername} in the system'.encode(FORMAT))

                #print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "timeline":
                #COMPLETED ON CLIENT SIDE NO NEED FOR ANYTHING ON SERVER SIDE
                print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "getusers":
                getUsers_msg = "\n".join([str(username) for username in usernames]) + "\n"
                to_send_message = f'{getUsers_msg} ###'

                broadcast(to_send_message.encode(FORMAT), None, 1, username)

                print(f"server read: TweetMessage {{username='{username}', msg='null', hashTags='null', operation='{cmd}'}}")
                #print("WARNING: NOTHING CODED FOR THIS YET")
            
            elif cmd == "exit":
                client_info = clients.pop(client_connection_socket)
                client_connection_socket.close

                usernames.pop(usernames.index(client_info["username"]))
                print(f"server read: TweetMessage{{ username='{client_info['username']}', msg='null', hashTags='null', operation='exit'}}")
                break
            
        except:
            client_info = clients.pop(client_connection_socket)
            client_connection_socket.close
            print(f"server read: TweetMessage{{ username='{client_info['username']}', msg='null', hashTags='null', operation='exit'}}")
            usernames.pop(usernames.index(client_info["username"]))
            #print(f"thread active:  {threading.activeCount() - 1}, number os users: {len(usernames)}") #TEST
            # broadcast(f'{client_info["username"]} left the chat!'.encode(FORMAT)) #TEST
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
