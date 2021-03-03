#==========================================
# Title:  ChatApp client
# Author: Aatu Laitinen
# Date:   1 March 2021
#==========================================

import socket
import threading
import time

room = input("Choose room to join('Room1','Room2','Room3'): ")
nickname = input("Choose a nickname: ")
#client connets to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1337))

def recieve():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if(message == 'ROOM'):
                client.send(room.encode('utf-8'))
            elif(message == 'NICK'):
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            print("Error occured!")
            time.sleep(1)
            client.close()
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
        else:
            client.send(message.encode('utf-8'))

#threading to allow multiple clients
recieve_thread = threading.Thread(target=recieve)
recieve_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()