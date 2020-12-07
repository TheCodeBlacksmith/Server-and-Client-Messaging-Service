# Server-and-Client-Messaging-Service

# Description

This program is a server and client messaging project developed and tested in Python. The client and server utilized a variant of the TCP protocol with some customization as to how specifically the client sent messages to the server and how the server accessed, understood and executed various commands based on the client's request. The software allows for multiple clients and also can understand hashtags like those that are found in large scale messaging platforms


# Included Files:

 * README.md - basic information for program execution
 * ttweetcl.py - client-side python source code file
 * ttweetsrv.py - server-side python source code file
 

# Details:

This program is a basic server and client messaging project devloped and tested in python 3.8.3. The client and server are fully contained
fully within ttweetcl.py and ttweetsrv.py respectively. Upon the intilalization of the server via ttweetsrv.py, clients
can be intialized via the ttweetcl.py file in individual terminal given that the correct port anfd server IP address is used.
The special "protocol" feature of this code base is an array of size 2 with the first index holding a character
representing the specific operation that the client wishes to perform on the server while the second index holds a <=150 
character message depending on if the first index holds the "u" or "" by default if the first index holds "d" for which
the server will return the last uploaded message from a clinet wihtin the current se4rver session. In the event that 
there is no previosuly uploaded message, the server will return the default message whihc is: "Empty Message".

The text output file (Sample.txt) will record all status report messages and messages for specific operations within the current 
server session. Report messages first list the side of connection they are being broadcast from (client or server) 
followed by their desgination which are under three catagories (defined in '[]' of report messages): 
    - GENERAL: designated for server initilaization, server receiving message, and client activation/deactivation
    - ERROR: designated for errors preventing server intialization, client intialization
      or if there is a violation of parameters or rules by the user.
    - CONNECTION: designated for client disconnection on server side and server deactivation
    Note: some report messages are not under catagory which are for completion of client procedure:
        * "Transmission Successfull..." : printed upon successfull client execution
        * "Received Message: <message>" : printed upon successfull client execution of download operation


# Compiling Instructions:

1. - open terminal in project folder location
2. - run python server file (ttweetsrv.py) on python 3.x.x to initalize python server 
     (Ex: $python ttweetsrv.py 13001)
3. - open a second terminal in project folder location 
4. - run python client file (ttweetcl.py) on python 3.x.x to initalize a python client 
     (Ex: $python ttweetcl.py -u 127.0.0.1 13001 "message here")
     (Ex: $python ttweetcl.py -d 127.0.0.1 13001)
5. - Upon successfull initialization of client (initilization message will be shown 
     on server terminal) the client and server are communicating and the single previous operation
     ("-u" for upload and "-d" for download last message) will be completedc and the client will be terminated


# Bugs / Limitations / Notes:

- Note: if the user submits "" it will reset the saved mesage as "Empty Message"
- Note: If running on personal machine (e.g: Windows) please make sure that Virus Protection does
  not block the text output file from updating. Not doing so may cause clinet side to hang (Issue occurs due to ransomware protection being enabled)
- Note: This software was built and tested on Python version 3.8.3 64-bit
