import socket
import threading
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

HOST = "0.0.0.0"
PORT = 12345

clients = {}  # Dictionnaire {socket: nom}
keys = {}  # Dictionnaire {socket: clé symétrique}

# Génération des clés RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Sérialisation de la clé publique
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def handle_client(client_socket, addr):
    """Gère un client : reçoit son nom et sa clé symétrique."""
    try:
        name = client_socket.recv(1024).decode("utf-8").strip()
        clients[client_socket] = name
        print(f"[+] Nouvelle connexion : {addr} - {name}")

        # Envoi de la clé publique au client
        client_socket.send(public_pem)

        # Réception de la clé symétrique chiffrée
        encrypted_key = client_socket.recv(256)
        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        keys[client_socket] = symmetric_key.decode()

        print(f"[+] Clé symétrique reçue pour {name}: {keys[client_socket]}")

        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"[{addr[0]} {name}] {message}")
            broadcast(f"[{addr[0]} {name}] {message}", client_socket)

    except:
        pass
    finally:
        print(f"[-] Déconnexion : {addr} - {clients.get(client_socket, 'Inconnu')}")
        clients.pop(client_socket, None)
        keys.pop(client_socket, None)
        client_socket.close()

def broadcast(message, sender_socket):
    """Envoie le message à tous les clients sauf l'émetteur."""
    for client in clients.keys():
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except:
                client.close()
                clients.pop(client, None)
                keys.pop(client, None)

def start_server():
    """Lance le serveur et accepte les connexions entrantes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Serveur démarré sur {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
