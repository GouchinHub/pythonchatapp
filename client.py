#==========================================
# Title:  ChatApp client
# Author: Aatu Laitinen
# Date:   6 March 2022
#==========================================

import socket
import threading
import time

nickname = input("Enter your nickname: ")

#client connets to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1234))

def establish_connection():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if(message == 'ROOM'):
                room = input("\nType the name of the room you want to join or create: ")
                client.send(room.encode('utf-8'))
            elif(message == 'NOROOM'):
                print(f'Room [{room}] doesnt exist')
                is_room_created = input(f'Do you want to create room: [{room}]? (yes / no): ')
                if is_room_created.lower() == 'yes':
                    client.send("YES".encode('utf-8'))
                else:
                    client.send("NO".encode('utf-8'))
                    close_client()
                    break
            elif(message == 'NICKNAME'):
                client.send(nickname.encode('utf-8'))
            elif(message == 'CONNECTED'):
                setup_complete()
                break
            elif(message == 'DISCONNECTED'):
                close_client()
                break
            else:
                print(f'{message}')
        except:
            print("Error occured!")
            close_client()
            break

def recieve():
    while True:
        try:
            print(client.recv(1024).decode('utf-8')) 
        except:
            close_client()
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        #@ functionality to whisper to other clients
        if message[len(nickname)+2:].startswith('@'):
            client.send(f'AT {nickname} {message[len(nickname)+3:]}'.encode('utf-8'))
        #/exit functionality to leave the server
        elif message[len(nickname)+2:] == '/exit':
            client.send('EXIT'.encode('utf-8'))
            client.close()
            break
        else:
            client.send(message.encode('utf-8'))

def close_client():
    print("Closing client...")
    time.sleep(1)
    client.close()
            
def setup_complete():
    #threading to allow multiple clients
    threading.Thread(target=recieve).start()
    threading.Thread(target=write).start()
    
threading.Thread(target=establish_connection).start()