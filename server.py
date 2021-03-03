#==========================================
# Title:  ChatApp server
# Author: Aatu Laitinen
# Date:   1 March 2021
#==========================================

import threading
import socket
import time

host = '127.0.0.1' #localhost
port = 1337

#creates the server using internet sockets
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

#Amount of available rooms on the server can be changed here
#changes are also needed to handle_room function
room1 = []
room2 = []
room3 = []
rooms = [room1,room2,room3]

allclients = []
nicknames = []

#broadcasts message to all the clients in the same room
def broadcast(roomindex,message):
    for client in rooms[roomindex]:
        client.send(message)

#sends private message to the target client if connected to server
def private_message(message_to,message_from, message_to_client):
    try:
        if message_to in nicknames:
            targetindex = nicknames.index(message_to)
            target_client = allclients[targetindex]
            target_client.send(f'FROM {message_from}: {message_to_client}'.encode('utf-8'))
        else:
            senderindex = nicknames.index(message_from)
            target_client = allclients[senderindex]
            target_client.send(f'user [{message_to}] does not exist'.encode('utf-8'))
    except:
        print("Error occured!")

#Handles the clients actions
def handle(client,roomindex):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('utf-8').startswith('AT'):
                #used to send private messages
                try:
                    data = msg.decode('utf-8')[2:].split(' ',3)
                    message_from = data[1]
                    target_client = data[2]
                    message_to_client = data[3]
                except:
                    continue
                private_message(target_client, message_from, message_to_client)
            elif msg.decode('utf-8') == ('EXIT'):
                #forces except to happen
                index[-1]
            else:
                #broadcasts message to others in same room
                broadcast(roomindex,message)
        except:
            #if the handling fails, the client connection is terminated, and client data removed
            #index = rooms[roomindex].index(client)
            rooms[roomindex].remove(client)
            index = allclients.index(client)
            allclients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            print(f'{nickname} disconnected')
            broadcast(roomindex, f'{nickname} has left the chat'.encode('utf-8'))
            break

#Recieves and processes the client connections
def recieve():
    while True:
        client, address = server.accept()
        print(f"connected with {str(address)}")
        #recieve client nickname and room
        client.send('ROOM'.encode('utf-8'))
        room = client.recv(1024).decode('utf-8')
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        #check nickname and room availability and add client to corresponding room
        roomindex = handle_room(room)
        if nickname in nicknames:
            client.send(f'Nickname [{nickname}] already taken'.encode('utf-8'))
            time.sleep(2)
            client.close()
            print(f"connection {str(address)} terminated")
            continue
        elif(roomindex == -1):
            client.send(f'Room [{room}] doesnt exist'.encode('utf-8'))
            time.sleep(2)
            client.close()
            print(f"connection {str(address)} terminated")
            continue
        else:
            nicknames.append(nickname)
            rooms[roomindex].append(client)
            allclients.append(client)
            print(f'Nickname of the client is {nickname}, Room: {room}')
            #creates a banner for the user to welcome and guide
            #sleep to help client handle
            client.send('########################################'.encode('utf-8'))
            time.sleep(0.01)
            client.send('#          Welcome to ChatApp!!        #'.encode('utf-8'))
            time.sleep(0.01)
            client.send('#  Use @ to whisper and /exit to leave #'.encode('utf-8'))
            time.sleep(0.01)
            client.send('########################################'.encode('utf-8'))
            time.sleep(1)
            broadcast(roomindex, f'{nickname} has joined the room: {room}!'.encode('utf-8'))

            #threading so we can handle multiple clients at the same time
            thread = threading.Thread(target=handle, args=(client,roomindex))
            thread.start()

#used to return desired index for room
def handle_room(room):
    if room == "Room1":
        return 0
    elif room == "Room2":
        return 1
    elif room == "Room3":
        return 2
    else:
        return -1

print("Server up and running!")
#main method to run the server
recieve()


