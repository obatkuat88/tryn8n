# tryn8n - Codespaces File Downloader

Aplikasi web Flask untuk mendownload file dari URL langsung ke Codespace Anda.

## Fitur
- 📥 Download file dari URL manapun
- 🔒 Secure filename handling dengan Werkzeug
- 💾 Auto-organize files di folder `/downloads`
- 🌐 Interface web yang user-friendly
- 🔗 Direct download link untuk setiap file

## Cara Menjalankan

### Opsi 1: Menggunakan Devcontainer (Recommended)
```bash
# Buka di GitHub Codespaces - app akan otomatis berjalan
```

### Opsi 2: Manual
```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

Atau gunakan script:
```bash
chmod +x run.sh
./run.sh
```

## Akses Aplikasi

- **URL**: http://localhost:8080
- **Port**: 8080
- **Download folder**: `/downloads` di root project

## Requirements
- Python 3.12+
- Flask 3.0.0
- Requests 2.31.0
- Werkzeug 3.0.1

## Troubleshooting

Jika port 8080 sudah digunakan:
```bash
PORT=3000 python app.py  # Ganti dengan port lain
```

## Walkthrough

Ringkasan singkat aplikasi dan cara pakainya:

- **Apa ini:** Aplikasi Flask sederhana untuk mendownload file dari URL dan menyimpannya ke folder `downloads/`.
- **File utama:** `app.py` (server), `run.sh` (script helper), `download_history.json` (log history).

### Persiapan

1. Buat virtual environment (direkomendasikan):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
./run.sh
# atau
python app.py
```

3. Buka browser ke `http://localhost:8080`.

### Endpoints penting

- `/` — Halaman utama dengan form untuk memasukkan URL file.
- `/download` (POST) — Endpoint yang menerima field `url` untuk memulai download.
- `/downloads/<filename>` — Mengunduh file yang sudah disimpan.
- `/history` — Menampilkan history download dan daftar file.
- `/delete/<filename>` — Menghapus file secara aman dan menghapus entri history terkait.

### Fitur Hapus File

- Penghapusan menggunakan `secure_filename` dan pemeriksaan `os.path.commonpath` untuk mencegah path traversal.
- Menghapus berkas fisik dari `downloads/` dan menghapus entri dari `download_history.json`.

### Testing cepat (hapus file)

1. Buat file uji:
```bash
mkdir -p downloads
echo test > downloads/test_delete.txt
```
2. Panggil endpoint hapus:
```bash
curl -v -L http://127.0.0.1:8080/delete/test_delete.txt
```
3. Pastikan file terhapus:
```bash
ls -la downloads
cat download_history.json
```

### Untuk produksi

- Gunakan WSGI server seperti `gunicorn` daripada Flask dev server.
- Tambahkan otentikasi sebelum mengekspos aplikasi secara publik.
