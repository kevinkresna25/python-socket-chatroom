import socket
import threading

HOST = '0.0.0.0'
PORT = 31234

clients = []    # list socket semua client
usernames = {}  # mapping socket -> nama user
lock = threading.Lock()

def broadcast_all(message: bytes):
    """Kirim message ke SEMUA client, tanpa kecuali."""
    with lock:
        for c in clients:
            try:
                c.sendall(message)
            except:
                pass

def handle_client(client_socket, client_address):
    # init
    client_socket.sendall(
        "👋 Selamat datang! Gunakan:\n"
        "  /nick <username>  → set nama\n"
        "  /list             → lihat user online\n"
        "  /exit             → keluar\n\n".encode('utf-8')
    )

    with lock:
        clients.append(client_socket)

    username = None
    while True:
        try:
            data = client_socket.recv(1024)
        except ConnectionResetError:
            break
        if not data:
            break

        msg = data.decode('utf-8').strip()

        # 1) set nickname
        if msg.startswith('/nick '):
            new_name = msg.split(' ', 1)[1].strip()
            username = new_name
            usernames[client_socket] = username
            client_socket.sendall(f"✅ Nama berhasil diubah: {username}\n".encode('utf-8'))
            continue

        # 2) list user
        if msg == '/list':
            with lock:
                names = ", ".join(usernames.values()) or "(kosong)"
            client_socket.sendall(f"👥 Pengguna online: {names}\n".encode('utf-8'))
            continue

        # 3) exit 
        if msg == '/exit':
            client_socket.sendall("👋 Bye!\n".encode('utf-8'))
            break

        # 4) get message
        if not username:
            client_socket.sendall(
                "⚠️ Silakan set username dulu dengan /nick <username>\n".encode('utf-8')
            )
            continue

        broadcast_all(f"{username}: {msg}\n".encode('utf-8'))

    with lock:
        if client_socket in clients:
            clients.remove(client_socket)
        left = usernames.pop(client_socket, None)
    client_socket.close()

    if left:
        broadcast_all(f"❌ {left} telah keluar.\n".encode('utf-8'))

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[LISTENING] Server berjalan di {HOST}:{PORT}")

    try:
        while True:
            client_sock, client_addr = server.accept()
            print(f"[CONNECT] {client_addr}")
            threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server dihentikan.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
