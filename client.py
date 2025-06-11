import socket
import threading
import sys

disconnected = threading.Event()

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("🔴 Terputus dari server.")
                disconnected.set()
                break
            print(data.decode('utf-8').strip())
        except:
            print("🔴 Error pada koneksi.")
            disconnected.set()
            break

def main():
    HOST = 'thelol.me'
    PORT = 12345

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except:
        print("❌ Gagal terhubung ke server.")
        return

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while not disconnected.is_set():
            msg = input()

            # \033[F  → pindah satu baris ke atas
            # \033[K  → clear sampai akhir baris
            sys.stdout.write('\033[F\033[K')
            sys.stdout.flush()

            if not msg.strip():
                continue

            sock.sendall(msg.encode('utf-8'))

            if msg.lower() in ('/exit', 'exit'):
                break

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sock.close()
        print("⚙️ Client keluar. Bye!")

if __name__ == "__main__":
    main()
