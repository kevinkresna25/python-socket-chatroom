import socket
import threading
import ssl
import re

HOST = '0.0.0.0'
PORT = 31234

# Regex untuk nickname: 3–16 chars, A–Z a–z 0–9 _
NICK_REGEX = re.compile(r'^[A-Za-z0-9_]{3,16}$')

clients   = []    # list SSL-wrapped client sockets
usernames = {}    # socket -> nickname
lock      = threading.Lock()

def broadcast_all(msg: bytes):
    """Kirim message ke SEMUA client"""
    with lock:
        for c in clients:
            try:
                c.sendall(msg)
            except:
                pass

def handle_client(ssock, addr):
    # Header
    welcome = (
        "👋 Selamat datang! Gunakan:\n"
        "  /nick <username>  → set nama (3-16 A-Za-z0-9_)\n"
        "  /list             → lihat user online\n"
        "  /exit             → keluar\n\n"
    )
    ssock.sendall(welcome.encode('utf-8'))

    with lock:
        clients.append(ssock)

    username = None
    try:
        while True:
            data = None
            try:
                data = ssock.recv(1024)
            except:
                break
            if not data:
                break

            msg = data.decode('utf-8', errors='ignore').strip()

            # 1) set nickname
            if msg.startswith('/nick '):
                new = msg.split(' ', 1)[1].strip()
                if not NICK_REGEX.match(new):
                    ssock.sendall("❌ Nick harus 3-16 karakter alnum/underscore.\n".encode('utf-8'))
                    continue
                with lock:
                    if new in usernames.values():
                        ssock.sendall("❌ Nick sudah dipakai, pilih yang lain.\n".encode('utf-8'))
                        continue
                username = new
                usernames[ssock] = username
                ssock.sendall(f"✅ Nick terdaftar: {username}\n".encode('utf-8'))
                continue

            # 2) list user
            if msg == '/list':
                with lock:
                    names = ", ".join(usernames.values()) or "(kosong)"
                ssock.sendall(f"👥 Online: {names}\n".encode('utf-8'))
                continue

            # 3) exit
            if msg == '/exit':
                ssock.sendall("👋 Bye!\n".encode('utf-8'))
                break

            # 4) get message
            if not username:
                ssock.sendall("⚠️ Set nick dulu: /nick <username>\n".encode('utf-8'))
                continue

            broadcast_all(f"{username}: {msg}\n".encode('utf-8'))

    finally:
        removed = None
        with lock:
            if ssock in clients:
                clients.remove(ssock)
            removed = usernames.pop(ssock, None)
        ssock.close()
        if removed:
            broadcast_all(f"❌ {removed} telah keluar.\n".encode('utf-8'))


def main():
    # Setup TLS context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    # Batasi TLS minimal 1.2
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    bindsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    finally:
        bindsock.close()

if __name__ == "__main__":
    main()
