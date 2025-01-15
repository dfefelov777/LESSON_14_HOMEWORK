Реализовать сервер, частично реализующий протокол HTTP, в частности методы GET и HEAD, добиться того, что код проходит предоставленные функциональны тесты. Архитектуру выбрать на свое усмотрение, исходя из вариантов,Ю рассмотренных на занятии. 
Провести нагрузочное тестирование с помощью ab или wrk


import socket
import threading
import os

HOST = 'localhost'
PORT=8080
DOCUMENT_ROOT = './www' #root folder for static files
def handle_request(client_socket):
    try:
        #todo
        # 1 get request
        # 2 get headers
        # 3 split headers to methods
        # 4 give back response index.html
        if method in ['GET', 'HEAD']:
            # create response and send it back
            return
     finally:
        client_socket.close()

def start_server():
    # 1. create sockets
    # 2. bind socket to address and port
    #3. in while loop create threads with function for handle_request

if __name__ == "__main__":
    starr_server()


#testing
ab -n 1000 -c 10 http://localhost:8080/index.html

wrk -t12 -c400 -d30s http://localhost:8080/index.html
