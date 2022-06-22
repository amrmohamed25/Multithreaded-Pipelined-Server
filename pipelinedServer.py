import time
from socket import *
import threading


# For every client we have a timestamp list to maintain the order of his/her requests
def threadedServer(connectionSocket, addr, ts, timestamps, timeoutt):
    timestamps.append(ts)  # appending in timestamps
    try:
        message = b""
        while True:  # This loop receives the request
            tempmessage = connectionSocket.recv(1024)
            message = message + tempmessage
            if not tempmessage or len(
                    tempmessage) < 1024:  # our limit is 1024 so if it is smaller than 1024 means the message ended
                break

        # The idea is to make only one thread can process request and reply to the client, at the same time another thread is spawned
        # and is receiving the next request
        if len(message) != 0:  # if there is no message means that there is no other requests
            while ts != min(timestamps):  # used to block threads to maintain order
                pass

            # Spawning new thread
            request_thread = threading.Thread(target=threadedServer,
                                              args=(connectionSocket, addr, time.time(), timestamps, timeoutt))
            request_thread.start()
            header = message.splitlines()[0]  # Getting first line which is the header
            request = header.split()[0]  # Getting the request either GET or POST
            print("\nRequest:\n")
            print(header)

            if request == b"GET":
                filename = message.split()[
                    1]  # Getting filename which the server will read from (if it exists in the server)
                f = open(filename[1:], "rb")  # Open the file in binary mode to read
                body = f.read()

                header_status = "HTTP/1.1 200 OK"
                header_info = {
                    "Content-Length": len(body),
                    "Keep-Alive": "timeout=%d,max=%d" % (timeoutt, 100),
                    "Connection": "Keep-Alive"
                }
                header_concat = "\r\n".join(
                    "%s:%s" % (item, header_info[item]) for item in header_info)  # adding \r\n between each line
                full_header = "%s\r\n%s\r\n\r\n" % (header_status, header_concat)
                print("Response:\n")
                print(full_header)

                response = full_header.encode() + body
                connectionSocket.sendall(response)  # sending header + data together

            elif request == b"POST":
                header_status = message.split(b"\r\n\r\n")[0]  # getting header
                full_header = header_status + b"\r\n\r\n"
                body = message.split(b"\r\n\r\n", 1)[1]  # getting data after empty line
                filename = full_header.split()[1].split(b"/")[
                    1]  # remove / from filename ex: /hello.txt to be hello.txt

                f = open(b"server_" + filename, "wb")  # opening to write in binary mode
                f.write(body)
                connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
                f.close()
                print("\nResponse:\n")
                print("HTTP/1.1 200 OK\r\n\r\n")

    except IOError as e:  # exception occured
        if str(e) == "timed out":  # if it is time out, then we will close the connection
            print("Timeout\n")
            connectionSocket.close()
        else:  # file not found
            try:
                connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                print("HTTP/1.1 404 Not Found\r\n\r\n")
            except:
                connectionSocket.close()

    if len(message) != 0:
        timestamps.remove(
            ts)  # removing the current ts to enable the next request to be processed and spawn another thread


if __name__ == '__main__':
    serverSocket = socket(AF_INET, SOCK_STREAM)  # Prepare a sever socket
    serverPort = 1234  # Our server port
    serverSocket.bind(('127.0.0.1', serverPort))  # server ip and port are binded together
    serverSocket.listen()  # server is listening for requests

    while True:
        print('\nReady to serve...')
        connectionSocket, addr = serverSocket.accept()  # accept user connection
        print("\nAddress:\n", addr)

        timeoutt = 50 / (threading.active_count())  # Timeout Heuristic
        ts = time.time()  # Time will be used in threadedServer to maintain the order of responses to requests

        connectionSocket.settimeout(timeoutt)  # setting timeout using our heuristic
        client_thread = threading.Thread(target=threadedServer,
                                         args=(connectionSocket, addr, ts, [], timeoutt))  # creating thread
        # client_thread.daemon = True
        client_thread.start()  # starting the thread
