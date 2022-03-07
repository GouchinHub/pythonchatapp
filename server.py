#==========================================
# Title:  ChatApp server
# Author: Aatu Laitinen
# Date:   6 March 2022
#==========================================

import threading
import socket
import time

NON_EXISTENT = -1
BUFFER_SIZE = 1024

host = '127.0.0.1' #localhost
port = 1234

#creates the server using internet sockets
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen()


class Room:
    def __init__(self, name):
        self.name = name
        self.clients = []
        
    def add_client(self, client):
        self.clients.append(client)
    
    def remove_client(self, client):
        self.clients.remove(client)


#Storage for room and client information
rooms_list = [Room("default_room")]
all_clients = []
nicknames = []


def search_client_connections():
    while True:
        client, address = server.accept()
        print(f"Client trying to connect from address: {str(address)}")
        threading.Thread(target=process_client_connections, args=(client, address)).start()
        
        
#Recieves and processes the client connections
def process_client_connections(client, address):
    #retrieve client nickname
    client.send('NICKNAME'.encode('utf-8'))
    nickname = client.recv(BUFFER_SIZE).decode('utf-8')
    
    #check nickname availability and add client to corresponding room
    if nickname in nicknames:
        client.send(f'Nickname [{nickname}] already taken'.encode('utf-8'))
        client.send("DISCONNECTED".encode('utf-8'))
        client.close()
        print(f"connection {str(address)} terminated")
        return
    
    #provide client with list of available rooms
    client.send('Available rooms: '.encode('utf-8'))
    for room in rooms_list:
        time.sleep(0.01)
        client.send((f'\t{room.name}').encode('utf-8'))
    
    time.sleep(0.01)
    
    #get and handle client chosen room
    client.send('ROOM'.encode('utf-8'))
    room_name = client.recv(BUFFER_SIZE).decode('utf-8')
    roomindex = get_room_index(room_name)
    
    if(roomindex == NON_EXISTENT):
        client.send('NOROOM'.encode('utf-8'))
        create = client.recv(BUFFER_SIZE).decode('utf-8')
        if (create == 'YES'):
            room = Room(room_name)
            rooms_list.append(room)
            print(f"Room [{room_name}] created by client: {nickname}")
        else:
            client.send("DISCONNECTED".encode('utf-8'))
            client.close()
            print(f"connection {str(address)} terminated")
            return
    
    #save client data to server
    nicknames.append(nickname)
    rooms_list[roomindex].add_client(client)
    all_clients.append(client)
    
    print(f'Nickname of the client is {nickname}, Room: {room_name}')
    create_banner(client)
    broadcast_to_clients_in_room(roomindex, f'{nickname} has joined the room: {room_name}!'.encode('utf-8'))
    
    client.send("CONNECTED".encode('utf-8'))
    handle_client_actions(client, roomindex)
        

#creates a banner for the user to welcome and guide
#uses sleep to help client handle incoming messages        
def create_banner(client):
    client.send('########################################'.encode('utf-8'))
    time.sleep(0.01)
    client.send('#          Welcome to ChatApp!!        #'.encode('utf-8'))
    time.sleep(0.01)
    client.send('#  Use @ to whisper and /exit to leave #'.encode('utf-8'))
    time.sleep(0.01)
    client.send('########################################'.encode('utf-8'))
    time.sleep(0.1)


def get_room_index(room_name):
    for index, room in enumerate(rooms_list):
        if room.name == room_name:
            return index
        
    return NON_EXISTENT
        

#Handles the clients actions
def handle_client_actions(client,roomindex):
    while True:
        try:
            message = client.recv(BUFFER_SIZE)
            
            #Handle private messages
            if message.decode('utf-8').startswith('AT'):
                try:
                    data = message.decode('utf-8')[2:].split(' ',3)
                    message_from = data[1]
                    target_client = data[2]
                    message_to_client = data[3]
                except:
                    continue
                private_message_client(target_client, message_from, message_to_client)
            #Handle client manual disconnect
            elif message.decode('utf-8') == ('EXIT'):
                close_client_connection(client,roomindex)
                break
            else:
                broadcast_to_clients_in_room(roomindex,message)
        except:
            close_client_connection(client,roomindex)
            break
        
       
def broadcast_to_clients_in_room(roomindex,message):
    for client in rooms_list[roomindex].clients:
        client.send(message)
        

def private_message_client(message_to,message_from, message_to_client):
    try:
        if message_to in nicknames:
            targetindex = nicknames.index(message_to)
            target_client = all_clients[targetindex]
            target_client.send(f'FROM {message_from}: {message_to_client}'.encode('utf-8'))
        else:
            senderindex = nicknames.index(message_from)
            target_client = all_clients[senderindex]
            target_client.send(f'user [{message_to}] does not exist'.encode('utf-8'))
    except:
        print("Error occured!")      
        
        
def close_client_connection(client,room_index):
    #the client connection is terminated, and client data removed
    rooms_list[room_index].remove_client(client)
    nickname = nicknames[all_clients.index(client)]
    nicknames.remove(nickname)
    all_clients.remove(client)
    client.close()
    print(f'{nickname} disconnected')
    broadcast_to_clients_in_room(room_index, f'{nickname} has left the chat'.encode('utf-8'))
        
     
print(f'Server up and running on port: {port}')
#main method to run the server
search_client_connections()


