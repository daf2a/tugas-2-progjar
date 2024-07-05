import socket
import threading
import logging
from time import gmtime, strftime

class CommandHandler:
    @staticmethod
    def send_time_response(connection):
        current_time = f"JAM {strftime('%H:%M:%S', gmtime())}\r\n"
        connection.sendall(current_time.encode())

    @staticmethod
    def send_quit_response(connection):
        quit_confirmation = "QUIT MESSAGE BERHASIL DITERIMA\n"
        connection.sendall(quit_confirmation.encode())
        connection.close()

    @staticmethod
    def send_unknown_response(connection):
        unknown_command_warning = "WARNING: COMMAND TIDAK DIKENAL\n"
        connection.sendall(unknown_command_warning.encode())

class ClientThread(threading.Thread):
    def __init__(self, socket, address):
        super().__init__()
        self.client_socket = socket
        self.client_address = address

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(32)
                if data:
                    command = data.decode().strip()
                    logging.warning(f"Data diterima: {command} dari {self.client_address}.")
                    if command.endswith('TIME'):
                        logging.warning(f"TIME command diterima dari {self.client_address}.")
                        CommandHandler.send_time_response(self.client_socket)
                    elif command.endswith('QUIT'):
                        logging.warning(f"QUIT command diterima dari {self.client_address}.")
                        CommandHandler.send_quit_response(self.client_socket)
                        break
                    else:
                        logging.warning(f"Perintah tidak dikenal {command} dari {self.client_address}.")
                        CommandHandler.send_unknown_response(self.client_socket)
                else:
                    break
            except OSError:
                break
        self.client_socket.close()

class TCPServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        super().__init__()
        self.host = host
        self.port = port
        self.client_threads = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.warning(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            logging.warning(f"Connection from {client_address}")

            client_thread = ClientThread(client_socket, client_address)
            client_thread.start()
            self.client_threads.append(client_thread)

def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    server = TCPServer()
    server.start()

if __name__ == "__main__":
    main()
