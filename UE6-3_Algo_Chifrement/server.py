import socket
import threading
from crypto import vigenere_decrypt

HOST = "0.0.0.0"
PORT = 12345
KEY = "SECRET"

clients = {}  # Dictionnaire {socket: nom}

def handle_client(client_socket, addr):
    """Gère un client : reçoit son nom et retransmet les messages."""
    try:
        name = client_socket.recv(1024).decode("utf-8").strip()
        clients[client_socket] = name
        print(f"[+] Nouvelle connexion : {addr} - {name}")

        while True:
            encrypted_data = client_socket.recv(1024).decode()
            if not encrypted_data:
                break  # Client déconnecté
            
            decrypted_message = vigenere_decrypt(encrypted_data, KEY)
            print(f"[{addr[0]} {name}] {decrypted_message}")

            # Envoyer à tous les autres clients
            broadcast(f"[{name}] {decrypted_message}", client_socket)

    except:
        print(f"[-] Erreur avec {addr} ({name})")
    finally:
        print(f"[-] Déconnexion : {addr} - {clients.get(client_socket, 'Inconnu')}")
        clients.pop(client_socket, None)
        client_socket.close()

def broadcast(message, sender_socket):
    """Envoie le message à tous les clients sauf l'émetteur."""
    for client in list(clients.keys()):  # Utilisation de list() pour éviter les erreurs de suppression
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except:
                client.close()
                clients.pop(client, None)

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
