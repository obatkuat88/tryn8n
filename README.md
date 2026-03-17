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