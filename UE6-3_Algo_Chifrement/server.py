import socket
import threading
import random
import tkinter as tk
from tkinter import scrolledtext
from crypto import vigenere_encrypt, vigenere_decrypt, normalize_key

P = 23
G = 5

class ChatServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.root = tk.Tk()
        self.root.title("Serveur")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack()

        self.input_box = tk.Entry(self.root)
        self.input_box.pack()

        self.send_button = tk.Button(self.root, text="Envoyer", command=self.server_send_message)
        self.send_button.pack()

    def diffie_hellman_private(self):
        return random.randint(2, P - 2)

    def diffie_hellman_shared(self, private_key, public_key):
        return (public_key ** private_key) % P

    def handle_client(self, client_socket, addr):
        try:
            client_socket.send(str(P).encode())
            client_socket.send(str(G).encode())

            private_key = self.diffie_hellman_private()
            public_key = (G ** private_key) % P
            client_socket.send(str(public_key).encode())

            client_public_key = int(client_socket.recv(1024).decode())
            shared_key = self.diffie_hellman_shared(private_key, client_public_key)
            key_str = normalize_key(shared_key)

            name = client_socket.recv(1024).decode().strip()
            self.clients[name] = (client_socket, key_str)

            self.text_area.insert(tk.END, f"[+] {name} connecté depuis {addr}\n")

            while True:
                encrypted_data = client_socket.recv(1024).decode()
                if not encrypted_data:
                    break

                decrypted_message = vigenere_decrypt(encrypted_data, key_str)
                self.text_area.insert(tk.END, f"[{name}] {decrypted_message}\n")

                if decrypted_message == "/users":
                    user_list = "Utilisateurs connectés: " + ", ".join(self.clients.keys())
                    client_socket.send(vigenere_encrypt(user_list, key_str).encode())
                elif decrypted_message.startswith("@"):  
                    target, msg = decrypted_message[1:].split(" ", 1)
                    if target in self.clients:
                        target_socket, target_key = self.clients[target]
                        target_socket.send(vigenere_encrypt(f"[Message privé] {name}: {msg}", target_key).encode())
                    else:
                        client_socket.send(vigenere_encrypt(f"Utilisateur {target} introuvable.", key_str).encode())
                else:
                    for client_name, (client, client_key) in self.clients.items():
                        if client_name != name:
                            client.send(vigenere_encrypt(f"[{name}] : {decrypted_message}", client_key).encode())
        except Exception as e:
            self.text_area.insert(tk.END, f"[-] Erreur avec {addr}: {e}\n")
        finally:
            self.text_area.insert(tk.END, f"[-] {name} déconnecté\n")
            self.clients.pop(name, None)
            client_socket.close()

    def server_send_message(self):
        message = self.input_box.get()
        self.text_area.insert(tk.END, f"[Serveur]: {message}\n")
        if message.startswith("@"): 
            target, msg = message[1:].split(" ", 1)
            if target in self.clients:
                target_socket, target_key = self.clients[target]
                target_socket.send(vigenere_encrypt(f"[Message privé] Serveur: {msg}", target_key).encode())
            else:
                self.text_area.insert(tk.END, f"[Serveur]: Utilisateur {target} introuvable.\n")
        else:
            for client_name, (client_socket, client_key) in self.clients.items():
                client_socket.send(vigenere_encrypt(f"[Serveur]: {message}", client_key).encode())
            self.input_box.delete(0, tk.END)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        threading.Thread(target=self.accept_connections, daemon=True).start()
        self.root.mainloop()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()
