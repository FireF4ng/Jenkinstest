import socket
import threading
import secrets
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

HOST = "127.0.0.1"
PORT = 12345

def receive_messages(sock):
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
    """Se connecte au serveur et sécurise l'échange de clé."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    name = input("Entrez votre nom : ").strip()
    client_socket.send(name.encode("utf-8"))

    # Réception de la clé publique
    public_pem = client_socket.recv(1024)
    public_key = serialization.load_pem_public_key(public_pem)

    # Génération d'une clé symétrique aléatoire
    KEY = secrets.token_hex(16)

    # Chiffrement de la clé avec RSA
    encrypted_key = public_key.encrypt(
        KEY.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    client_socket.send(encrypted_key)

    print(f"[+] Clé symétrique envoyée : {KEY}")

    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    while True:
        message = input("")
        if not message.strip():
            continue  # Ne pas envoyer de messages vides

        client_socket.sendall(message.encode())

if __name__ == "__main__":
    start_client()
