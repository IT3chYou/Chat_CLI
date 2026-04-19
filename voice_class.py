from pygame import mixer
import time
import os


class Voice:
    def __init__(self):
        self.dir_name = "voice"
        self.coming_message = f"tweet.mp3"
        self.own_message = "own.mp3"
        self.upload_message = "upload_message.mp3"
        self.exit_message = "error.mp3"
        self.connection_error_message = "error.mp3"
        self.connect_message = f"login1.mp3"
        self.active_session_message = "ac_ses_login.mp3"
        self.active_session_exit_message = "ac_ses_exit.mp3"
        self.voice_clients = {}
       

        
        try:
            mixer.init()
        except Exception as e:
            print(f"Uyarı: Pygame mixer başlatılamadı. Hata: {e}")


    def file_check(self):
        file = os.path.exists(self.dir_name)
        if not file:
            print("File Not Found")

    def play_voice(self, wav_file):
        full_path = os.path.join(self.dir_name, wav_file)
        try:
            # mixer.init() çağrısı __init__ içine taşındı.
            mixer.music.load(full_path)
            mixer.music.play()

            while mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Ses çalınırken hata oluştu: {e}")

    def open_voice(self):
        self.play_voice(self.connect_message)

    def close_voice_and_con_err(self):
        self.play_voice(self.exit_message)


