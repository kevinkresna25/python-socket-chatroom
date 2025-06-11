import socket
import ssl
import threading
import sys

disconnected = threading.Event()

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("🔴 Terputus.")
                disconnected.set()
                break
            print(data.decode('utf-8').strip())
        except:
            print("🔴 Error koneksi.")
            disconnected.set()
            break

def main():
    HOST = 'thelol.me'
    PORT = 31234

    # SSL context untuk self-signed/CA-less
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode    = ssl.CERT_NONE

    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = context.wrap_socket(raw, server_hostname=HOST)
    try:
        ssock.connect((HOST, PORT))
    except:
        print("❌ Gagal terhubung.")
        return

    threading.Thread(target=receive_messages, args=(ssock,), daemon=True).start()

    try:
        while not disconnected.is_set():
            msg = input()
            # clear echo input
            sys.stdout.write('\033[F\033[K'); sys.stdout.flush()

            if not msg.strip():
                continue

            ssock.sendall(msg.encode())
            if msg.lower() in ('/exit', 'exit'):
                break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        ssock.close()
        print("⚙️ Client keluar. Bye!")

if __name__ == "__main__":
    main()
