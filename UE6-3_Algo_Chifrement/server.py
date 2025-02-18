import socket
import threading
import random
import tkinter as tk
from tkinter import scrolledtext
from crypto import vigenere_encrypt, vigenere_decrypt, normalize_key

P = 23
G = 5

clients = {}

HOST = "0.0.0.0"
PORT = 12345

def diffie_hellman_private():
    return random.randint(2, P - 2)

def diffie_hellman_shared(private_key, public_key):
    return (public_key ** private_key) % P

def handle_client(client_socket, addr, text_area):
    try:
        client_socket.send(str(P).encode())
        client_socket.send(str(G).encode())

        private_key = diffie_hellman_private()
        public_key = (G ** private_key) % P
        client_socket.send(str(public_key).encode())

        client_public_key = int(client_socket.recv(1024).decode())
        shared_key = diffie_hellman_shared(private_key, client_public_key)
        key_str = normalize_key(shared_key)

        name = client_socket.recv(1024).decode().strip()
        clients[name] = (client_socket, key_str)

        text_area.insert(tk.END, f"[+] {name} connecté depuis {addr}\n")

        while True:
            encrypted_data = client_socket.recv(1024).decode()
            if not encrypted_data:
                break

            decrypted_message = vigenere_decrypt(encrypted_data, key_str)
            text_area.insert(tk.END, f"[{name}] {decrypted_message}\n")

            if decrypted_message == "/users":
                user_list = "Utilisateurs connectés: " + ", ".join(clients.keys())
                client_socket.send(vigenere_encrypt(user_list, key_str).encode())

            elif decrypted_message.startswith("@"):
                parts = decrypted_message.split(" ", 1)
                if len(parts) < 2:
                    continue
                target, msg = parts
                target = target[1:]

                if target in clients:
                    target_socket, target_key = clients[target]
                    target_socket.send(vigenere_encrypt(f"[Message privé] {name}: {msg}", target_key).encode())
                else:
                    client_socket.send(vigenere_encrypt(f"Utilisateur {target} introuvable.", key_str).encode())

            else:
                for client_name, (client, client_key) in clients.items():
                    if client_name != name:
                        client.send(vigenere_encrypt(f"[{name}] {decrypted_message}", client_key).encode())

    except Exception as e:
        text_area.insert(tk.END, f"[-] Erreur avec {addr}: {e}\n")

    finally:
        text_area.insert(tk.END, f"[-] {name} déconnecté\n")
        clients.pop(name, None)
        client_socket.close()

def server_send_message():
    """Permet au serveur d'envoyer un message global."""
    while True:
        message = input("Serveur: ")
        for client_name, (client_socket, client_key) in clients.items():
            client_socket.send(vigenere_encrypt(f"Serveur: {message}", client_key).encode())

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    root = tk.Tk()
    root.title("Serveur")

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_area.pack()

    threading.Thread(target=server_send_message, daemon=True).start()

    def accept_connections():
        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr, text_area), daemon=True).start()

    threading.Thread(target=accept_connections, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    start_server()
