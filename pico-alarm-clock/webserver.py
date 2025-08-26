import socket
import network
import asyncio

import config

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

def http_response_bytes(body: bytes, status="200 OK", content_type="text/html"):
    headers = [
        f"HTTP/1.1 {status}",
        "Server: PicoW",
        f"Content-Length: {len(body)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        ""
    ]
    header_bytes = "\r\n".join(headers).encode()
    return header_bytes + body

def http_response(body: str, status="200 OK", content_type="text/html"):
    body_bytes = body.encode("utf-8")
    return http_response_bytes(body_bytes, status, content_type)

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

            # print(config.data)
            body = await get_document("index.html") % (config.data["alarm"] or "not set")
            try:
                client.send(http_response(body))
            except Exception as e:
                print(f"SEND FAILED: {e}")
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
            
