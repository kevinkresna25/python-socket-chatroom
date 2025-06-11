# python-socket-chatroom

A secure, multi-client chatroom application using Python sockets, with nickname validation and TLS encryption, packaged in Docker for easy deployment.

---

## 🔥 Fitur Utama

* **Multi-client broadcast**: Kirim pesan real-time ke semua client yang terhubung.
* **Perintah chat**:

  * `/nick <username>` → Set atau ubah nickname (3–16 karakter alnum/underscore)
  * `/list` → Lihat daftar pengguna online
  * `/exit` → Disconnect dari server
* **Validasi nickname**: Hanya alfanumerik dan underscore, panjang 3–16, unik per sesi.
* **Enkripsi TLS**: Semua komunikasi server-client terenkripsi menggunakan sertifikat X.509.
* **Dockerized**: Server siap dijalankan dalam container via Docker & Docker Compose.

---

## ⚙️ Persyaratan

* Python 3.10 atau lebih baru
* OpenSSL (untuk generate self-signed cert di development)
* Docker & Docker Compose (untuk deployment container)

---

## 🛠️ Instalasi & Setup

1. **Clone repo**

   ```bash
   git clone https://github.com/your-username/python-socket-chatroom.git
   cd python-socket-chatroom
   ```

2. **(Opsional) Generate sertifikat self-signed**

   ```bash
   openssl req -newkey rsa:2048 -nodes \
     -keyout certs/server.key \
     -x509 -days 365 \
     -out certs/server.crt \
     -subj "/CN=yourdomain.com"
   ```

   Hasilnya: `server.key` dan `server.crt`.

---

## 🚀 Menjalankan Server

Ada dua cara untuk menjalankan **server**:

### 1) Via Docker Compose (direkomendasikan)

```bash
./start.sh
```

> Skrip `start.sh` akan melakukan:
>
> * `docker compose down`
> * `docker compose up -d --build`
> * `docker image prune -f`

### 2) Manual (tanpa Docker)

```bash
# Pastikan sertifikat sudah ada di folder
python server.py
```

Server akan mendengarkan koneksi di port **31234**.

---

## 🚀 Menjalankan Client

Untuk menjalankan **client**, cukup jalankan di mesin terpisah (atau Windows/Linux/macOS) yang dapat mengakses server:

```bash
python client.py
```

> * Pastikan variabel `HOST` di `client.py` diatur ke alamat server (misal `thelol.me` atau IP publik).
> * Setelah terkoneksi, gunakan perintah chat (`/nick`, `/list`, `/exit`) sesuai instruksi di layar.

Contoh sesi:

```
👋 Selamat datang!
  /nick <username>  → set nama
  /list             → lihat user online
  /exit             → keluar

/nick Anda
✅ Nick terdaftar: Anda
Anda: Hello everyone!
/list
👥 Online: Anda, Teman
/exit
👋 Bye!
```

---

## 📁 Struktur Direktori

```text
.
├── certs/
│   ├── server.crt
│   └── server.key
├── client.py
├── server.py
├── Dockerfile
├── docker-compose.yml
├── start.sh
└── LICENSE
```

---

## 📜 License

MIT © Kevin Kresna, 2025. [MIT License](LICENSE)
