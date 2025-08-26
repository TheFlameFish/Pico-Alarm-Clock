import socket
import network
import asyncio

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

sock = socket.socket()
sock.bind(addr)
sock.listen(1)

async def get_document(name: str):
    try:
        with open(f"/site/{name}", "r") as file:
            return file.read()
        
    except Exception as e:
        print(f"WARN: Failed to open file {name}.\n{e}")
        return f"Error: File not found: {name}"

async def run_server():
    print("Listening on:", addr)
    sock.setblocking(False)

    while True:
        try:
            client, client_addr, = sock.accept()
            print("Client connected from", client_addr)
            request = client.recv(1024)
            print(request)

            request = str(request)

            if request.find("/test") == 6:
                print("User went to test path")

            response = await get_document("index.html") % "03:00"
            client.send(response)
            client.close()
        except OSError as e:
            try:
                if client: # Keeps giving error EAGAIN, but seems to work.
                    client.close() 
                    # print("Connection closed. Error: ",e)
                    client = None
            except NameError:
                pass

        await asyncio.sleep(0)
            
