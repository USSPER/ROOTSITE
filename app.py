from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os
import requests
import yt_dlp

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = 'downloads'
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        download_url = request.form.get("download_url")
        if download_url:
            try:
                # Intenta descargar un video de YouTube
                if "youtube.com" in download_url or "youtu.be" or "https://www.facebook.com/" in download_url:
                    ydl_opts = {'outtmpl': os.path.join(app.config["UPLOAD_FOLDER"], '%(title)s.%(ext)s'),'no-check-certificate': True,'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([download_url])
                    return redirect(url_for('index'))
                else:
                    # Si no es un enlace de YouTube, intenta descargar un archivo normal
                    filename = download_url.split("/")[-1]
                    response = requests.get(download_url, stream=True)
                    response.raise_for_status()
                    with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    return redirect(url_for('index'))
            except (requests.exceptions.RequestException, yt_dlp.utils.DownloadError) as e:
                return render_template("index.html", error="Error al descargar el archivo: {}".format(e))
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files)

@app.route('/downloads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)