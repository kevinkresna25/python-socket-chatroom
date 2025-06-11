import socket
import ssl
import threading
import sys

HOST = 'thelol.me'
PORT = 31234
ENCODING = 'utf-8'

def receive_messages(sock: ssl.SSLSocket, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            data = sock.recv(1024)
            if not data:
                print("🔴 Terputus.")
                stop_event.set()
                break
            print(data.decode(ENCODING, 'ignore').strip())
        except Exception:
            if not stop_event.is_set():
                print("🔴 Error koneksi.")
                stop_event.set()
            break

def main():
    stop_event = threading.Event()

    # SSL context untuk self-signed
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = context.wrap_socket(raw, server_hostname=HOST)
    try:
        ssock.connect((HOST, PORT))
    except Exception:
        print("❌ Gagal terhubung.")
        return

    # Thread penerima pesan
    threading.Thread(target=receive_messages, args=(ssock, stop_event), daemon=True).start()

    try:
        while not stop_event.is_set():
            msg = input().strip()
            # Hapus echo baris input
            sys.stdout.write('\033[F\033[K')
            sys.stdout.flush()

            if not msg:
                continue
            try:
                ssock.sendall(msg.encode(ENCODING))
            except Exception:
                print("🔴 Gagal kirim.")
                break

            if msg.lower() in ('/exit', 'exit'):
                stop_event.set()
                break

    except (KeyboardInterrupt, EOFError):
        stop_event.set()
    finally:
        try:
            ssock.close()
        except:
            pass
        print("⚙️ Client keluar. Bye!")

if __name__ == "__main__":
    main()
