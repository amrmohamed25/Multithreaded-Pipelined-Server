import threading
import time
from socket import *
import sys
import os

def pipelinedRequest(request,filename,server_host,ts):
    
    
    try:
        current_request = "%s /%s HTTP/1.1\r\nHost: %s\r\n\r\n" % (request, filename, server_host)
        print(current_request)
        print(cached_files.keys())
        if current_request in cached_files.keys():
            cached_response = cached_files.get(current_request)[0]
            print(b"Response: \n" + cached_response)
            if request == "GET" and cached_response != b"HTTP/1.1 404 Not Found\r\n\r\n":
                cached_data = cached_files.get(current_request)[1]
                # print(b"File Data: \n" + cached_data)

        else:           
            # client_socket = socket(AF_INET, SOCK_STREAM)
            # client_socket.connect((server_host, int(server_port)))
            
            if request == "GET":
                print("Not cached\n")
                # while ts!=min(timestamps):
                #     pass
                while(ts!=min(timestamps)):
                    pass
                client_socket.sendall(current_request.encode())
                # time.sleep(1)
                timestamps.remove(ts)
                print(time.time())
                data=b""
               
                while True:
                    tempdata = client_socket.recv(1024)
                    data=data+tempdata
                    if not tempdata or len(tempdata) <1024:
                        break
                
                header = data.split(b"\r\n\r\n")[0]
                header=header+b"\r\n\r\n"
                outputdata = data.split(b"\r\n\r\n")[1]
                if data == b"HTTP/1.1 404 Not Found\r\n\r\n" or header==b"HTTP/1.0 404 Not Found\r\n\r\n":
                    print(data)
                else:
                    f = open("client_"+filename,"wb")
                    f.write(outputdata)
                    f.close()
                    # print("lol")
                    # time.sleep(1)
                    cached_files[current_request] = [header, outputdata]
                    # print(cached_files[current_request][1])
                # timestamps.remove(ts)
            elif request == "POST":
                try:
                    f = open(filename, 'rb')
                    outputdata = f.read()
                    new_request=current_request.encode()
                    new_request += outputdata
                    # print(outputdata)
                    while ts!=min(timestamps):
                        pass
                    client_socket.sendall(new_request)
                    # time.sleep(3)
                    # ts=time.time()
                    
                    # time.sleep(1)
                    # print(time.time())
                    # response_status=b""
                    # while True:
                    #     tempdata = client_socket.recv(1024)
                    #     response_status=response_status+tempdata
                    #     if not tempdata or len(tempdata) <1024:
                    #         break
                    response_status = client_socket.recv(1024)
                    timestamps.remove(ts) 
                    # print(b"post",response_status)
                    print("sad")
                    # cached_files[current_request] = [response_status]
                    # print(cached_files.get(current_request)[0])
                    # timestamps.remove(ts) 
                except Exception as e:
                    print(e)
                    print("Can't find file to upload !")
    except Exception as e:
        print(e)
        print("Timeout occured!!")
        

cached_files = {}

index = 0
# inputfilename = sys.argv[1] ###TODO: uncomment
inputfilename = "input.txt"
try:
    file = open(inputfilename, 'r')
except:
    print("File does't exist !!!")
    sys.exit(-1)
request_socket={}
lines=file.readlines()
pipelined_threads=[]
timestamps=[]
for next_line in lines:
    mystring = next_line.strip().split()
    #cache l requests hna w ashoof hconnect wla la2
    print(mystring)
    server_host = mystring[2]
    try:
        server_port = mystring[3]
    except:
        server_port = 80
    #eny mmokn a3ml thread blocking lw7dha
    filename = mystring[1]
    request = mystring[0]
    ts=time.time()
    timestamps.append(ts) 
    if server_port not in request_socket:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_host, int(server_port)))
        request_socket[server_port]=client_socket
    else:
        client_socket=request_socket.get(server_port)
    pipelined_thread=threading.Thread(target=pipelinedRequest, args=(request,filename,server_host,ts))
    # pipelined_thread.daemon = True
    # time.sleep(2)
    pipelined_thread.start()
    # time.sleep(2)
    pipelined_threads.append(pipelined_thread)
    # for mythread in pipelined_threads:
    #     mythread.join()
    # pipelined_thread.join()

for mythread in pipelined_threads:
    mythread.join()
client_socket.close()
print("This client finished")
file.close()

# GET register.php 127.0.0.1 (1234)
# GET wireshark-labs/INTRO-wireshark-file1.html 128.119.245.12 (80)
# GET hello.html 127.0.0.1 (1234)
# GET hello.html 127.0.0.1 (1234)
