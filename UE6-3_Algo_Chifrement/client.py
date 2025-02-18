import socket
import threading
import random
import tkinter as tk
from tkinter import simpledialog, scrolledtext
from crypto import vigenere_encrypt, vigenere_decrypt, normalize_key

P = 23
G = 5

HOST = "127.0.0.1"
PORT = 12345

def diffie_hellman_private():
    return random.randint(2, P - 2)

def diffie_hellman_shared(private_key, public_key):
    return (public_key ** private_key) % P

def receive_messages(sock, key, text_area):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            decrypted_message = vigenere_decrypt(data, key)
            text_area.insert(tk.END, f"{decrypted_message}\n")
        except:
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    P = int(client_socket.recv(1024).decode())
    G = int(client_socket.recv(1024).decode())

    private_key = diffie_hellman_private()
    public_key = (G ** private_key) % P
    client_socket.send(str(public_key).encode())

    server_public_key = int(client_socket.recv(1024).decode())
    shared_key = diffie_hellman_shared(private_key, server_public_key)
    key_str = normalize_key(shared_key)

    root = tk.Tk()
    root.title("Chat sécurisé")

    name = simpledialog.askstring("Nom", "Entrez votre nom :", parent=root)
    root.title("Chat sécurisé - " + name)
    client_socket.send(name.encode())

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_area.pack()

    input_box = tk.Entry(root)
    input_box.pack()

    def send_message():
        message = input_box.get()
        text_area.insert(tk.END, f"[{name}]: {message}\n")
        if message and key_str:
            encrypted_message = vigenere_encrypt(message, key_str)
            client_socket.send(encrypted_message.encode())
            input_box.delete(0, tk.END)

    send_button = tk.Button(root, text="Envoyer", command=send_message)
    send_button.pack()

    def request_users():
        """Demande la liste des utilisateurs."""
        client_socket.send(vigenere_encrypt("/users", key_str).encode())

    users_button = tk.Button(root, text="Liste des utilisateurs", command=request_users)
    users_button.pack()

    threading.Thread(target=receive_messages, args=(client_socket, key_str, text_area), daemon=True).start()
    root.mainloop()

    client_socket.close()

if __name__ == "__main__":
    start_client()
