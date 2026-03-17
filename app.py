from flask import Flask, request, send_from_directory, render_template_string
import requests
import os
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Codespaces File Downloader</title></head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h1>🚀 Codespaces File Downloader</h1>
        <p>Paste any direct file URL below</p>
        <form method="post" action="/download">
            <input type="text" name="url" placeholder="https://example.com/file.zip" 
                   style="width:600px; padding:10px; font-size:16px;" required>
            <br><br>
            <button type="submit" style="padding:12px 30px; font-size:18px;">Download Now</button>
        </form>
    </body>
    </html>
    """)

@app.route("/download", methods=["POST"])
def download_file():
    url = request.form.get("url").strip()
    
    # Get clean filename
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or "downloaded_file"
    filename = secure_filename(filename)
    
    # Avoid overwriting
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        base, ext = os.path.splitext(filename)
        i = 1
        while os.path.exists(os.path.join(DOWNLOAD_DIR, f"{base}_{i}{ext}")):
            i += 1
        filename = f"{base}_{i}{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Stream download (works for huge files too)
    print(f"Downloading: {url} → {filename}")
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192 * 4):
            f.write(chunk)

    download_link = f"/downloads/{filename}"
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Download Ready</title></head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h1>✅ Download Complete!</h1>
        <p><strong>File:</strong> {filename}</p>
        <p><strong>Size:</strong> {os.path.getsize(filepath) / (1024*1024):.2f} MB</p>
        
        <h2><a href="{download_link}" download style="font-size:24px; color:green;">
            ⬇️ Click here to download
        </a></h2>
        
        <p><a href="/">← Download another file</a></p>
        <p style="color:#666; font-size:14px;">
            This link works as long as your Codespace is running and port 8080 is public.
        </p>
    </body>
    </html>
    """)

# Serve the downloaded files
@app.route("/downloads/<path:filename>")
def serve_download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)