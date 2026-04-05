class Screen_Record:
    def __init__(self):
        self.file_name = "video"
        self.ffmpeg_process = None
        self.http_process = None

    # ----------------------------
    # HTTP SERVER
    # ----------------------------
    def start_http_server(self):
        if self.http_process:
            return

        if not os.path.exists(self.file_name):
            os.makedirs(self.file_name)

        # index.html oluştur
        with open(os.path.join(self.file_name, "index.html"), "w", encoding="utf-8") as f:
            f.write("<html>...HLS JS CODE...</html>")

        cmd = ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0", "--directory", self.file_name] \
            if os.name == "nt" else \
            ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0", "--directory", self.file_name]

        self.http_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # ----------------------------
    # FFMPEG
    # ----------------------------
    def start_ffmpeg(self, monitor_index=0):
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            return

        # eski HLS temizliği
        for f in os.listdir(self.file_name):
            if f.endswith(".ts") or f.endswith(".m3u8"):
                os.remove(os.path.join(self.file_name, f))

        monitor = get_monitors()[monitor_index % len(get_monitors())]

        if os.name == "nt":
            ffmpeg_cmd = ["ffmpeg", "-f", "gdigrab", ...]
        else:
            ffmpeg_cmd = ["ffmpeg", "-f", "x11grab", ...]  # Linux

        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # ----------------------------
    # STOP
    # ----------------------------
    def stop_ffmpeg(self):
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=3)
                if self.ffmpeg_process.poll() is None:
                    self.ffmpeg_process.kill()
            except Exception as e:
                print("FFmpeg stop error:", e)
            finally:
                self.ffmpeg_process = None  # 🔹 bu satır çok önemli

    def stop_http_server(self):
        if self.http_process:
            self.http_process.terminate()
            self.http_process.wait(timeout=3)
            self.http_process = None