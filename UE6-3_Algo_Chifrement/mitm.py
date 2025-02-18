import socket

HOST = "127.0.0.1"
PORT = 12345

def start_mitm():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("[*] MITM en attente de connexion...")

    victim_socket, addr = server.accept()
    print(f"[+] Victime connectée : {addr}")

    while True:
        data = victim_socket.recv(1024)
        if not data:
            break
        print(f"[MITM] Intercepté : {data.decode()}")

    victim_socket.close()
    server.close()

if __name__ == "__main__":
    start_mitm()
