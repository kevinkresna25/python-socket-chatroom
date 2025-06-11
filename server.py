import socket
import threading
import ssl
import re

HOST = '0.0.0.0'
PORT = 31234
ENCODING = 'utf-8'
NICK_REGEX = re.compile(r'^[A-Za-z0-9_]{3,16}$')

clients = set()         # set of SSL sockets
usernames: dict = {}    # sslsocket -> nickname
lock = threading.Lock()

def send(sock, text: str):
    """Send UTF-8 encoded text to satu client, ignore jika error."""
    try:
        sock.sendall(text.encode(ENCODING))
    except Exception:
        pass

def broadcast(text: str):
    """Kirim ke semua client."""
    data = text.encode(ENCODING)
    with lock:
        for c in list(clients):
            try:
                c.sendall(data)
            except Exception:
                pass

def handle_client(ssock: ssl.SSLSocket, addr):
    send(ssock,
        "👋 Selamat datang!\n"
        "  /nick <username>  → set nama (3-16 A-Za-z0-9_)\n"
        "  /list             → lihat user online\n"
        "  /exit             → keluar\n\n"
    )

    with lock:
        clients.add(ssock)

    username = None
    try:
        while True:
            try:
                data = ssock.recv(1024)
            except Exception:
                break
            if not data:
                break

            msg = data.decode(ENCODING, 'ignore').strip()

            # 1) Set nickname
            if msg.startswith('/nick '):
                new = msg.split(' ', 1)[1].strip()
                if not NICK_REGEX.match(new):
                    send(ssock, "❌ Nick harus 3-16 karakter alnum/underscore.\n")
                    continue
                with lock:
                    if new in usernames.values():
                        send(ssock, "❌ Nick sudah dipakai, pilih yang lain.\n")
                        continue
                    usernames[ssock] = new
                username = new
                send(ssock, f"✅ Nick terdaftar: {username}\n")
                continue

            # 2) List user
            if msg == '/list':
                with lock:
                    names = ", ".join(usernames.values()) or "(kosong)"
                send(ssock, f"👥 Online: {names}\n")
                continue

            # 3) Exit
            if msg == '/exit':
                send(ssock, "👋 Bye!\n")
                break

            # 4) Chat
            if not username:
                send(ssock, "⚠️ Set nick dulu: /nick <username>\n")
                continue
            broadcast(f"{username}: {msg}\n")

    finally:
        with lock:
            clients.discard(ssock)
            removed = usernames.pop(ssock, None)
        ssock.close()
        if removed:
            broadcast(f"❌ {removed} telah keluar.\n")

def main():
    # Setup TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bindsock:
        bindsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bindsock.bind((HOST, PORT))
        bindsock.listen(5)
        print(f"[LISTENING TLS] {HOST}:{PORT}")

        try:
            while True:
                client, addr = bindsock.accept()
                ssock = context.wrap_socket(client, server_side=True)
                print(f"[CONNECT] {addr}")
                threading.Thread(target=handle_client, args=(ssock, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server dihentikan.")

if __name__ == "__main__":
    main()
