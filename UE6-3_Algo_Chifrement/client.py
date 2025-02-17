import socket
import threading
from crypto import vigenere_encrypt, vigenere_decrypt

KEY = "SECRET"
HOST = "127.0.0.1"
PORT = 12345

def receive_messages(sock):
    """Reçoit et affiche les messages du serveur."""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("[!] Connexion fermée par le serveur.")
                break
            print(data)
        except:
            print("[!] Erreur de connexion. Déconnexion...")
            break

def start_client():
    """Se connecte au serveur et permet d'envoyer des messages."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    name = input("Entrez votre nom : ").strip()
    client_socket.send(name.encode("utf-8"))

    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    try:
        while True:
            message = input("")
            if not message.strip():
                continue  # Ignore les messages vides

            encrypted_message = vigenere_encrypt(message, KEY)
            print(f"[+] Message crypté : {encrypted_message}")

            client_socket.sendall(encrypted_message.encode())

    except KeyboardInterrupt:
        print("\n[!] Déconnexion...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
