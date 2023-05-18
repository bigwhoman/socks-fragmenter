import socket
import socketserver
import select
from time import sleep

class MyDynamicSocksProxyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client_address = self.client_address
        print(f"Client: {client_address}")

        # Read the initial SOCKS handshake message from the client
        data = self.request.recv(4096)
        print("data ---> ",data)

        if not data:
            return

        # Check if the SOCKS version is supported (only SOCKS5 in this example)
        if data[0] != 0x05:
            return

        # print("req ---> ",self.request)
        self.request.sendall(b'\x05\x00')

        # Read the client's connection request
        data = self.request.recv(4096)
        if not data:
            return

        # Parse the destination address and port from the client's connection request
        address_type = data[3]
        if address_type == 0x01:  # IPv4
            dest_addr = socket.inet_ntop(socket.AF_INET, data[4:8])
            dest_port = int.from_bytes(data[8:10], 'big')
        elif address_type == 0x03:  # Domain name
            domain_length = data[4]
            dest_addr = data[5:5 + domain_length].decode()
            dest_port = int.from_bytes(data[5 + domain_length:7 + domain_length], 'big')
        else:
            return

        # Connect to the destination server
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((dest_addr, dest_port))




        # Send the server's response to the client's connection request
        self.request.sendall(b'\x05\x00\x00' + data[3:])

        # Forward data between the client and destination server
        first_request = True
        try:
            while True:
                readable, _, _ = select.select([self.request, remote_socket], [], [], 1)
                if self.request in readable:
                    data = self.request.recv(4096)
                    if len(data) == 0:
                        break

                    # Fragment the first request's payload into 1-byte fragments
                    if first_request:
                        # human_readable = binascii.unhexlify(data.hex()).decode('utf-8', 'replace')
                        # print(f"First request payload (TCP hello): {human_readable}")
                        for byte in data:
                            remote_socket.sendall(bytes([byte]))
                            sleep(0.005)
                        first_request = False
                    else:
                        remote_socket.sendall(data)
                if remote_socket in readable:
                    data = remote_socket.recv(4096)
                    if len(data) == 0:
                        break
                    self.request.sendall(data)
        finally:
            remote_socket.close()






def main():
    host, port = "localhost", 1357
    server = socketserver.ThreadingTCPServer((host, port), MyDynamicSocksProxyHandler)
    print(f"Dynamic SOCKS proxy server listening on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()


