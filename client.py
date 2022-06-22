from socket import *
import sys

cached_files = {}
inputfilename = sys.argv[1]

try:
    file = open(inputfilename, 'r')  # open input file
except:  # if the file doesn't exit
    print("File does't exist !!!")
    sys.exit(-1)

while True:
    next_line = file.readline()  # iterate on the file lines and process each line
    if not next_line:
        break

    mystring = next_line.strip().split()  # parse the line by removing \n and spaces
    server_host = mystring[2]  # extract server host address
    try:
        server_port = mystring[3]  # extract server host port number
    except:
        server_port = 80  # default port number

    filename = mystring[1]  # extract filename
    request = mystring[0]  # extract request GET/POST

    try:
        current_request = "%s /%s HTTP/1.0\r\nHost: %s:%s\r\n\r\n" % (
            request, filename, server_host, server_port)  # construct request format
        print("\nRequest:\n", current_request)

        if current_request in cached_files.keys():  # check if the request is cached
            cached_response = cached_files.get(current_request)[0]
            print("Already in cache:\n")
            print("Request:\n", current_request)
            print("Response: \n")
            print(cached_response)
            if request == "GET" and cached_response != b"HTTP/1.0 404 Not Found\r\n\r\n":  # print data if found
                cached_data = cached_files.get(current_request)[1]
                print("\nFile Data: \n")
                print(cached_data)

        else:
            client_socket = socket(AF_INET, SOCK_STREAM)  # create a new socket if the request is not cached
            client_socket.connect((server_host, int(server_port)))

            print("Not cached\n")
            if request == "GET":
                client_socket.sendall(current_request.encode())  # send request to server
                data = b""
                
                while True:  # receive the server's response
                    tempdata = client_socket.recv(1024)
                    data = data + tempdata
                    if not tempdata or len(
                            tempdata) < 1024:  # our limit is 1024 so if it is smaller than 1024 means the message ended
                        break

                header = data.split(b"\r\n\r\n")[0]  # parsing to get the header from the response
                header = header + b"\r\n\r\n"
                body = data.split(b"\r\n\r\n", 1)[1]  # parsing to get the body from the response
                if header == b"HTTP/1.0 404 Not Found\r\n\r\n" or header == b"HTTP/1.1 404 Not Found\r\n\r\n":  # if server doesn't have the file
                    print("Response: ")
                    print(header)
                else:
                    if '/' in filename:
                        filename = filename.split('/')[1]
                    f = open("client_" + filename, "wb")  # write the body contents of the response in a file
                    f.write(body)
                    f.close()
                    print("\nResponse:")
                    print(header)
                    cached_files[current_request] = [header,
                                                     body]  # cache the request, response status and body contents

            elif request == "POST":
                try:
                    f = open(filename, 'rb')  # open file required to be uploaded
                    body = f.read()
                    new_request = current_request.encode()
                    new_request += body
                    client_socket.sendall(new_request)  # send the header and file to be uploaded to the server
                    response_status = client_socket.recv(1024)  # receive response status
                    print("Response:\n")
                    print(response_status)
                    cached_files[current_request] = [response_status]  # cache the request and response status
                except:
                    print("Can't find file to upload !")  # if the filename in the input file in not valid or not found
            client_socket.close()
    except Exception as e:
        print("Error occurred !")
        print(e)

print("\nThis client finished\n")
file.close()
