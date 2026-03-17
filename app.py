from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for, jsonify
import requests
import os
import json
import shutil
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
HISTORY_FILE = "download_history.json"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Helper functions for history management
def load_history():
    """Load download history from JSON file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """Save download history to JSON file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_to_history(filename, url, file_size):
    """Add a download entry to history"""
    history = load_history()
    entry = {
        "filename": filename,
        "url": url,
        "size_mb": round(file_size / (1024*1024), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "completed"
    }
    history.insert(0, entry)  # Add to front
    save_history(history)

def get_file_size(filename):
    """Get file size in bytes"""
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0

def format_file_size(size_bytes):
    """Format file size to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

@app.route("/")
def index():
    file_count = len([f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))])
    total_size = format_file_size(sum(os.path.getsize(os.path.join(DOWNLOAD_DIR, f)) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))))
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Codespaces File Downloader</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
            .container { max-width: 700px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #333; margin-bottom: 10px; }
            .header p { color: #666; }
            .nav-buttons { display: flex; gap: 10px; margin-bottom: 30px; justify-content: center; }
            .nav-buttons a { padding: 8px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-size: 14px; transition: 0.3s; }
            .nav-buttons a:hover { background: #764ba2; }
            .form-group { margin-bottom: 20px; }
            input[type="text"], textarea { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; font-family: inherit; transition: 0.3s; }
            input[type="text"]:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; transition: 0.3s; font-weight: bold; }
            button:hover { background: #764ba2; }
            .stats { display: flex; gap: 20px; margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; }
            .stat { flex: 1; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 File Downloader</h1>
                <p>Fast & Easy Download Manager</p>
            </div>
            
            <div class="nav-buttons">
                <a href="/">📥 Download</a>
                <a href="/history">📋 History ({{ file_count }} files)</a>
            </div>

            <form method="post" action="/download">
                <div class="form-group">
                    <input type="text" name="url" placeholder="https://example.com/file.zip" required>
                </div>
                <button type="submit">⬇️ Download File</button>
            </form>

            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{{ file_count }}</div>
                    <div class="stat-label">Files Downloaded</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ total_size }}</div>
                    <div class="stat-label">Total Size</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, file_count=file_count, total_size=total_size)

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

    # Get final file size and add to history
    file_size = os.path.getsize(filepath)
    add_to_history(filename, url, file_size)

    download_link = f"/downloads/{filename}"
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download Complete</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
            .container {{ background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; max-width: 500px; text-align: center; }}
            .success-icon {{ font-size: 60px; margin-bottom: 20px; }}
            h1 {{ color: #333; margin-bottom: 10px; }}
            .file-info {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: left; }}
            .info-row {{ margin: 10px 0; }}
            .info-label {{ color: #666; font-size: 14px; }}
            .info-value {{ color: #333; font-weight: bold; word-break: break-all; }}
            .actions {{ display: flex; gap: 10px; margin-top: 20px; }}
            .btn {{ flex: 1; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; text-decoration: none; transition: 0.3s; }}
            .btn-primary {{ background: #667eea; color: white; }}
            .btn-primary:hover {{ background: #764ba2; }}
            .btn-secondary {{ background: #eee; color: #333; }}
            .btn-secondary:hover {{ background: #ddd; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>Download Complete!</h1>
            
            <div class="file-info">
                <div class="info-row">
                    <div class="info-label">Filename:</div>
                    <div class="info-value">{filename}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Size:</div>
                    <div class="info-value">{format_file_size(file_size)}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">Time:</div>
                    <div class="info-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
            </div>

            <div class="actions">
                <a href="{download_link}" download class="btn btn-primary">⬇️ Download</a>
                <a href="/history" class="btn btn-secondary">📋 History</a>
            </div>

            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                <a href="/" style="color: #667eea;">← Download another file</a>
            </p>
        </div>
    </body>
    </html>
    """)

# Serve the downloaded files
@app.route("/downloads/<path:filename>")
def serve_download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

@app.route("/history")
def history():
    """Display download history and file management"""
    history_list = load_history()
    
    # Get current files in directory
    files_in_dir = os.listdir(DOWNLOAD_DIR)
    file_details = {}
    for f in files_in_dir:
        filepath = os.path.join(DOWNLOAD_DIR, f)
        if os.path.isfile(filepath):
            file_details[f] = {
                "size": format_file_size(os.path.getsize(filepath)),
                "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
            }
    
    history_html = ""
    if history_list:
        history_html = "<tr><th>File</th><th>Size</th><th>Date</th><th>Action</th></tr>"
        for entry in history_list:
            filename = entry.get('filename', 'Unknown')
            size = entry.get('size_mb', 0)
            timestamp = entry.get('timestamp', 'N/A')
            delete_btn = f'<a href="/delete/{filename}" onclick="return confirm(\'Delete {filename}?\')" style="color: #e74c3c; text-decoration: none;">🗑️ Delete</a>'
            history_html += f"<tr><td>{filename}</td><td>{size} MB</td><td>{timestamp}</td><td>{delete_btn}</td></tr>"
    else:
        history_html = "<tr><td colspan='4' style='color: #999; padding: 40px;'>No downloads yet</td></tr>"
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download History</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
            .header h1 {{ color: #333; }}
            .nav-btn {{ padding: 8px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; transition: 0.3s; }}
            .nav-btn:hover {{ background: #764ba2; }}
            .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }}
            .stat-card {{ background: #f5f5f5; padding: 20px; border-radius: 5px; text-align: center; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            tr:hover {{ background: #f9f9f9; }}
            .delete-section {{ margin-top: 30px; padding-top: 30px; border-top: 2px solid #eee; }}
            .delete-btn {{ padding: 8px 12px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; transition: 0.3s; }}
            .delete-btn:hover {{ background: #c0392b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Download History</h1>
                <a href="/" class="nav-btn">📥 Download</a>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{len(history_list)}</div>
                    <div class="stat-label">Total Downloads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(file_details)}</div>
                    <div class="stat-label">Files Stored</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{format_file_size(sum(os.path.getsize(os.path.join(DOWNLOAD_DIR, f)) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))))}</div>
                    <div class="stat-label">Total Size</div>
                </div>
            </div>

            <h2 style="margin-bottom: 15px; color: #333;">Recent Downloads</h2>
            <table>
                {history_html}
            </table>
        </div>
    </body>
    </html>
    """)

@app.route("/delete/<filename>")
def delete_file(filename):
    """Delete a downloaded file"""
    # Normalize filename and build absolute path
    from werkzeug.utils import secure_filename as _secure
    safe_name = _secure(filename)
    abs_download_dir = os.path.abspath(DOWNLOAD_DIR)
    abs_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, safe_name))

    # Security: ensure file is inside the downloads directory
    try:
        if os.path.commonpath([abs_download_dir, abs_path]) != abs_download_dir:
            return "Invalid file", 403
    except ValueError:
        return "Invalid file", 403

    if os.path.exists(abs_path) and os.path.isfile(abs_path):
        try:
            os.remove(abs_path)
            print(f"Deleted: {safe_name}")
        except Exception as e:
            print(f"Error deleting {safe_name}: {e}")

    # Also remove from history (if present)
    try:
        history = load_history()
        new_history = [h for h in history if h.get('filename') != safe_name]
        if len(new_history) != len(history):
            save_history(new_history)
    except Exception:
        pass

    return redirect(url_for('history'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Not Found</title>
        <style>
            body { font-family: Arial; text-align: center; margin-top: 50px; }
            h1 { color: #e74c3c; }
            a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>404 - Page Not Found</h1>
        <p>Sorry, the page you're looking for doesn't exist.</p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """), 404

@app.errorhandler(Exception)
def handle_error(error):
    """Handle general errors"""
    error_msg = str(error)
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error</title>
        <style>
            body {{ font-family: Arial; text-align: center; margin-top: 50px; background: #fff3cd; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; border: 2px solid #e74c3c; }}
            h1 {{ color: #e74c3c; }}
            p {{ color: #666; line-height: 1.6; }}
            a {{ color: #667eea; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Error Occurred</h1>
            <p><strong>Details:</strong> {error_msg}</p>
            <p><a href="/">← Back to Home</a></p>
            <p style="font-size: 12px; color: #999;">Check the server logs for more information.</p>
        </div>
    </body>
    </html>
    """), 500

if __name__ == "__main__":
    # Allow overriding host/port/debug via environment variables
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    debug = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)