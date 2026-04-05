import socket
import threading
import os
import subprocess
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align
from voice_class import Voice
from help import Help
from scree_record_stuff import Screen_Record
from voice_server import VoiceListen
import time
import datetime
from queue import Queue
from screeninfo import get_monitors
import webbrowser



class Sender:
    def __init__(self) -> None:
        self.ui_queue = Queue()
        self.strtime = datetime.datetime.now()
        self.voice_listen = VoiceListen()
        self.console = Console()
        self.prompt = "[bold red]<[/bold red][bold green]^[/bold green][bold red]>[/bold red] "
        self.connection = None
        self.ip_address = ""
        self.port = 0
        self.nickname = ""
        self.selected_color = "white"
        self.password = ""
        self.encode = "utf-8"
        self.active_sessions = []
        self.active_users = []
        self.receiving_file = True
        self.file_obj = None
        self.true_message = []
        self.false_message = []
        self.rich_prompt = Prompt()
        self.center_panel_color = "light_sky_blue1"
        self.right_panel_color = "medium_purple3"
        self.colors = [
            "red", "green", "yellow",
            "blue", "magenta", "cyan", "white", "bright_red", "bright_green", "bright_yellow", "bright_blue",
            "bright_magenta",
            "bright_cyan", "orange1", "orange3", "dark_orange", "orange_red1", "gold1", "gold3", "gold4",
            "deep_pink1", "deep_pink2", "deep_pink3", "hot_pink", "hot_pink2", "hot_pink3",
            "violet", "violet_red", "medium_purple", "medium_purple2", "blue_violet",
            "dodger_blue1", "dodger_blue2", "dodger_blue3", "sky_blue1", "sky_blue2", "sky_blue3",
            "spring_green1", "spring_green2", "spring_green3", "sea_green1", "sea_green2", "sea_green3",
            "turquoise2", "turquoise4", "dark_turquoise", "medium_turquoise",
            "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4",
            "aquamarine1", "aquamarine2", "aquamarine3", "pale_green1", "pale_green3",
            "khaki1", "khaki3", "khaki4", "light_goldenrod1", "light_goldenrod3",
            "salmon1", "indian_red", "orchid", "plum1", "plum3",
            "slate_blue1", "slate_blue3", "steel_blue1", "steel_blue3"
        ]
        self.voice = Voice()
        self.help = Help()
        self.video = Screen_Record()
        self.tweet = True
        self.voice_ip_address = ""
        self.voice_port = 0
        self.print_lock = threading.Lock()




    def list_monitors(self):
        monitors = get_monitors()
        for i, m in enumerate(monitors):
            print(f"[{i}] {m.width}x{m.height} Offset: ({m.x},{m.y})")
        return monitors

    def clear_prompt(self):

        # Alt satır (╰─$)
        self.console.file.write("\033[F")  # 1 satır yukarı
        self.console.file.write("\033[K")  # satırı sil

        # Üst satır (╭─⚡nick)
        self.console.file.write("\033[F")
        self.console.file.write("\033[K")

        self.console.file.flush()


    def input_(self):
        with self.print_lock:
            line1 = f"╭─⚡ {self.nickname} "
            line2 = "╰─$ "

            for char in line1:
                self.console.print(char, end="")
                time.sleep(0.02)

            self.console.print()

            for char in line2:
                self.console.print(char, end="")
                time.sleep(0.02)

        return self.console.input()

    def right_message_panel(self, message,title:str):
        with self.print_lock:
            self.clear_prompt()
            panel = Panel(message,border_style=self.right_panel_color,title=title,padding=(0, 2),width=30)
            self.console.print(Align.right(panel))




    def center_message_panel(self, message, title="Chat"):
        with self.print_lock:
            self.console.print()
            panel = Panel(str(message),border_style=self.center_panel_color,width=50,title=title)
            self.console.print(panel, justify="center")






    def ui_loop(self):
        while True:
            event, data = self.ui_queue.get()


            if event == "ASK_UPLOAD_CONFIRM":
                answer = Prompt.ask("Please Answer The Question : ( Yes/Or Anything ) ",
                    console=self.console)

                if answer.lower() == "yes" and self.connection is not None:
                    self.connection.send(answer.encode())
                else:
                    text = "[red]You Don't Take The Upload![/red]"
                    self.ui_queue.put(("CONFIRM_MESSAGE", text))



            elif event == "TAKE_USERS":
                self.right_message_panel(data, "Online Users")

            elif event == "TAKE_SPECIAL_MESSAGE":
                self.right_message_panel(data, "Private Message")

            elif event == "UPLOAD_MESSAGE":
                self.right_message_panel(data, "Upload Information")

            elif event == "CONFIRM_MESSAGE":
                self.right_message_panel(data, "Upload Confirmation")

            elif event == "ACTIVE_SESSION_MESSAGE":
                self.right_message_panel(data, "Session Update")

            elif event == "FORMAT_ERROR":
                self.right_message_panel(data, "Format Error")

            elif event == "CHANGED_PANEL_COLOR":
                self.right_message_panel(data, "Panel Color Updated")

            elif event == "UNKNOW_COLOR":
                self.right_message_panel(data, "Color Not Found")

            elif event == "LIST_PANEL_COLORS":
                self.right_message_panel(data, "Available Panel Colors")

            elif event == "SENDED_MESSAGE":
                self.right_message_panel(data, "Message Sent")

            elif event == "SERVER_MESSAGE":
                self.center_message_panel(data, "System Notice")

            elif event == "ERROR":
                self.center_message_panel(data, "System Error")


            elif event == "NORMAL_MESSAGE":
                self.center_message_panel(data)



    def connect_to_server(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(5)  # 5 saniye içinde bağlanamazsa hata versin
            self.connection.connect((self.ip_address, self.port))
            self.connection.settimeout(None) # Bağlandıktan sonra timeout'u kaldır
            full_message = f"{self.nickname}"
            self.connection.send(full_message.encode())
            self.voice.open_voice()  # play_voice içerisnde var ve open_voice ile içinde file_name Bilgisi Olduğundan Direk Çalışacak
        except Exception as e:
            self.ui_queue.put(("ERROR", f"[red]Connection Error:[/red] {e}"))

    def send_message(self):
        if not self.connection:
                self.ui_queue.put(("ERROR", "[red]No connection to server.[/red]"))
                return
        if self.connection:
            try:
                while True:
                    if self.connection is None:
                        break

                    message = self.input_()
                    if not message:
                        continue
                    self.console.print("\n")
                    if self.active_sessions:
                        if message.lower() in ["return", "chat"] and self.active_sessions: #buda Aktif Sesiondan Çıkmak İçin Açan Kişi Kapatıyor Unutma
                            for target in self.active_sessions:
                                self.connection.send(f"EXIT_SESSION {target}".encode(self.encode))
                            self.active_sessions = []  # session temizlenir
                            self.voice.play_voice(self.voice.active_session_exit_message)
                            continue       #

                        if message.startswith("exit") and self.active_sessions:#Kullanıcı Silme bu Karıştıma
                            _, user_exit = message.split(" ", 1)
                            # user_exit = ''.join(c for c in user_exit if c.isprintable()).strip()
                            for c in ''.join(user_exit):
                                if c.isprintable():
                                    c.strip()
                            if user_exit in self.active_sessions:
                                self.active_sessions.remove(user_exit)
                                self.connection.send(f"REMOVE_USER {user_exit}".encode(self.encode))
                                text = f"The User Delete in Group Conversation {user_exit}"
                                self.ui_queue.put(("ACTIVE_SESSION_MESSAGE",text))
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)




                    if message.startswith("center_panel_color"):

                        if len(message.split(" ",2)) != 2:
                            text = f"FORMAT ERRORt"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        _, panel_color = message.split(" ", 2)
                        if panel_color in self.colors:
                            text = f"The Panel Color Changed to {panel_color}"
                            self.ui_queue.put(("CHANGED_PANEL_COLOR",text))
                            self.center_panel_color = panel_color
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)


                        else:
                            text = f" Sorry Unknow Colors {panel_color}/n See All The Color (list_panel_colors)"
                            self.ui_queue.put(("UNKNOW_COLOR",text))



                    elif message.startswith("right_panel_color"):

                        if len(message.split(" ",2)) != 2:
                            text = f"FORMAT ERRORt"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        _, panel_color = message.split(" ", 2)
                        if panel_color in self.colors:
                            text = f"The Panel Color Changed to {panel_color}"
                            self.ui_queue.put(("CHANGED_PANEL_COLOR",text))
                            self.right_panel_color = panel_color
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)


                        else:
                            text = f" Sorry Unknow Colors {panel_color}/n See All The Color (list_panel_colors)"
                            self.ui_queue.put(("UNKNOW_COLOR",text))

                    elif message.startswith("message_voice"):
                        if len(message.split(" ", 1)) != 2:
                            text = f"FORMAT ERROR"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        _, bool_value = message.split(" ", 1)
                        if bool_value.lower() == "true":
                            self.tweet = True
                            self.voice.play_voice(self.voice.own_message)
                        else:
                            self.tweet = False
                            self.voice.play_voice(self.voice.own_message)



                    elif message.startswith("create_voice_chat"):
                        threading.Thread(target=self.voice_listen.listen_to_server,args=(self.voice_listen.ip_address, self.voice_listen.port),daemon=False).start()
                        self.voice.open_voice()


                    elif message.startswith("close_voice_chat"):
                        threading.Thread(target=self.voice_listen.exit_the_server,daemon=True).start()
                        self.voice.close_voice_and_con_err()




                    elif message.lower() == "list_panel_colors":
                        text = '()'.join(self.colors)
                        self.ui_queue.put(("LIST_PANEL_COLORS",text))
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)

                    elif message.startswith("select"):
                        if len(message.split()) != 2:
                            text = f"FORMAT ERROR"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        _, *users = message.split()
                        self.active_sessions = users
                        user_list_str = " ".join(users)
                        self.connection.send(f"SELECTED_USER {user_list_str}".encode())



                    elif message[0:6] == "users:":

                        if len(message.split()) <= 2:
                            text = f"FORMAT ERROR"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue


                        command, receiver_name, content = message.split(maxsplit=2)  # İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur
                        full_message = f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        self.connection.send(full_message.encode(self.encode))
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)

                        text = "The Message has been sent."
                        self.ui_queue.put(("SENDED_MESSAGE",text))




                    elif message.startswith("users"):
                        full_message = f'GET_USERS {self.nickname}'
                        self.connection.send(full_message.encode())

                    elif message.startswith("cmd"):
                        try:
                            command = message.split(maxsplit=1)[1]  # cmd <komut>
                            # Windows ise cmd, değilse bash
                            shell = "cmd" if os.name == "nt" else "bash"
                            # Komutu subprocess ile çalıştır, sadece kendi local makinede

                            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE, text=True, encoding="latin1")
                            output, error = process.communicate()  # Komut tamamlanana kadar bekle
                            if output:
                                self.ui_queue.put(("SERVER_MESSAGE", f"[green]Output:[/green]\n{output}"))
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                            if error:
                                self.ui_queue.put(("ERROR", f"[red]Error:[/red]\n{error}"))
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                        except Exception as e:
                            self.ui_queue.put(("ERROR", f"[red]Command execution error:[/red] {e}"))



                    elif message.startswith("start_record"):
                        parts = message.split()
                        try:
                            monitor_index = int(parts[1])
                        except (IndexError, ValueError):
                            monitor_index = 0

                        file_name = "video"

                        # HTTP server sadece bir kere başlatılır
                        if not self.video.http_process:  # self.video.http_process HTTP server objesi
                            if not os.path.exists(file_name):
                                os.makedirs(file_name)

                            # index.html oluştur
                            with open(os.path.join(file_name, "index.html"), "w", encoding="utf-8") as video_file:
                                video_file.write("""<!DOCTYPE html>
                    <html>
                    <head>
                    <meta charset="UTF-8">
                    <title>Canlı Ekran Yayını</title>
                    </head>
                    <body>
                    <video id="video" controls autoplay width="800"></video>
                    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
                    <script>
                        const video = document.getElementById('video');
                        if (Hls.isSupported()) {
                            const hls = new Hls();
                            hls.loadSource('stream.m3u8');
                            hls.attachMedia(video);
                            hls.on(Hls.Events.MANIFEST_PARSED, function () {
                                video.play();
                            });
                        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                            video.src = 'stream.m3u8';
                            video.addEventListener('loadedmetadata', function () {
                                video.play();
                            });
                        }
                    </script>
                    </body>
                    </html>""")

                            # HTTP serveri başlat
                            if os.name == "nt":
                                threading.Thread(target=self.video.start_http_server, args=(file_name,), daemon=True).start()
                            else:
                                threading.Thread(target=self.video.start_http_server_linux, args=(file_name,), daemon=True).start()

                            time.sleep(2)  # serverin açılması için kısa bekleme
                            self.connection.sendall(f"[URL:] http://{self.ip_address}:8080/index.html".encode())

                        # FFmpeg her seferinde başlatılır
                        if os.name == "nt":
                            threading.Thread(target=self.video.start_ffmpeg, args=(file_name, monitor_index), daemon=True).start()
                        else:
                            threading.Thread(target=self.video.start_ffmpeg_linux, args=(file_name, monitor_index), daemon=True).start()

                        self.ui_queue.put(("SERVER_MESSAGE", "[green]FFMPEG Was Started[/green]"))
                        self.clear_prompt()

                    elif message.startswith("stop_record"):
                        try:
                            self.video.stop_ffmpeg()  # sadece FFmpeg duracak, HTTP server devam eder
                            self.ui_queue.put(("SERVER_MESSAGE", "[red]FFMPEG stopped![/red]"))
                            self.clear_prompt()
                        except Exception as e:
                            self.ui_queue.put(("ERROR", f"[red]{e}[/red]"))





                    elif message.startswith("cls"):
                        os.system("cls" if os.name == "nt" else "clear")
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)
                    elif message.startswith("help"):
                        self.help.show_help()
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)
                        continue

                    elif message.startswith("upload"):
                        if len(message.split()) != 3:
                            text = f"FORMAT_ERROR"
                            self.ui_queue.put(("FORMAT_ERROR",text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        try:
                            _, directory, file_name = message.split(" ", 2)
                            full_path = os.path.join(directory, file_name)

                            if not os.path.exists(full_path):
                                self.false_message.append("[red]The file does not exist! Please check the path.[/red]")
                                continue
                            size = os.path.getsize(full_path)
                            self.true_message.append(
                                f"[green]The file '{file_name}' exists. Sending To Server [The File Size:{size}][/green]")
                            self.connection.send(f"U_START {directory} {file_name} {size}\n".encode(
                                self.encode))  # Dosya Bilgileri Gönderildi
                            with open(full_path,
                                      "rb") as f:  # Dosya Açıldı Okunan Veriler Kontrollu Şekilde Gönderilicek
                                while True:
                                    chunk = f.read(4096)
                                    if not chunk:
                                        break
                                    self.connection.sendall(chunk)

                            # Mesaj Sağda Gözüksün Diye
                            self.true_message.append(f"[bold green]File '{file_name}' successfully to Send Server [/bold green]")
                            edited_text = Text.from_markup(" ".join(self.true_message),justify="center")  # Metini Editlemek İçin
                            self.ui_queue.put(("UPLOAD_MESSAGE",edited_text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            self.true_message.clear()

                        except Exception as e:
                            self.false_message.append(f"[red]Upload error:[/red] {e}")
                            edited_text = Text.from_markup(" ".join(self.false_message),justify="center")  # Metini Editlemek İçin
                            self.ui_queue.put(("UPLOAD_MESSAGE",edited_text))
                            self.false_message.clear()



                    elif message.lower().strip() in ["exit", "q"]:
                        self.connection.send('exit'.encode())
                        self.voice.close_voice_and_con_err()
                        break
                    else:
                        self.connection.sendall(message.encode())  # Sendall İle Tüm Veri Gönderilir

            except Exception as e:
                self.ui_queue.put(("ERROR", f"[red]Error:[/red]\n{e}"))

        else:
            self.ui_queue.put(("ERROR", "[red]No connection to server. Please connect first.[/red]"))

    def receive_message(self):
        if self.connection is None:
                self.ui_queue.put(("ERROR", "[red]Hata: Soket objesi oluşturulamadı.[/red]"))
                return

        try:
            while True:

                try:
                    response = self.connection.recv(4096).decode(errors="ignore").strip()
                    if not response:

                        self.ui_queue.put(("ERROR", "[red]Server disconnected.[/red]"))
                        break
                except ConnectionResetError:
                    self.voice.close_voice_and_con_err()
                    break







                if response.startswith("[URL:]"):
                    url = response.split("[URL:]")[1].strip()
                    self.ui_queue.put(("SERVER_MESSAGE", f"Live Stream URL: {url}"))
                    # Eğer otomatik açmak istersen:
                    webbrowser.open(url)
                    continue



                if response.startswith("TAKE_USERS_SESSION"):
                    _, user_connections = response.split(" ", 1)  # 'user_connections' örnek: ["Yasir/Talha/Reyyan"]
                    self.active_sessions = [user.strip() for user in user_connections.split("/")]
                    self.voice.play_voice(self.voice.active_session_message)
                    """
                    # ["Yasir","Reyyan","Talha"]
                    # print(f"[green]Active session started with: {', '.join(self.active_sessions)}[/green]")
                    # İstemcide Active User Geçtikten Sonra İsim Benzerliğinden Dolayı Active Users Geliyor Zaten O Sebeple Yukarıdakini Yazmaya Gerek Yok Ama Yazmak Gerekse Bilde Panel İle Sağ Tarafta Yazdırmayı Unutma
                    """


                if response.startswith("TAKE_USERS"):
                    _, user_list = response.split(" ", 1)
                    user_list = ''.join(c for c in user_list if c.isprintable()).strip()  # bazen strip bile göremeyebilir
                    self.ui_queue.put(("TAKE_USERS",user_list))
                    if self.tweet:
                        self.voice.play_voice(self.voice.own_message)
                    continue



                if response.startswith("TAKE_SPECIAL_MESSAGE"):
                    _, special_message = response.split(" ", 1)
                    message = special_message.strip()
                    self.ui_queue.put(("TAKE_SPECIAL_MESSAGE",message))
                    continue


                if response.startswith("UPLOAD_MESSAGE"):
                    _, question = response.split(maxsplit=1)
                    message = ''.join(c for c in question if c.isprintable()).strip()
                    self.ui_queue.put(("UPLOAD_MESSAGE", message))
                    self.ui_queue.put(("ASK_UPLOAD_CONFIRM", None))
                    continue


                if response.startswith("UPLOAD_FILE"):
                    _, file_name = response.split(" ", 1)
                    self.file_obj = open(file_name, "wb")
                    # Sunucuya "hazırım" sinyali gönder
                    self.connection.send(b"ready")  # Burda Bana Verileri Gönder Diyorum
                    while True:
                        chunk = self.connection.recv(4096)
                        if b"END" in chunk:
                            chunk = chunk.replace(b"END", b"")
                            self.file_obj.write(chunk)
                            self.file_obj.close()
                            self.receiving_file = False
                            self.file_obj = None
                            break

                        self.file_obj.write(chunk)
                    self.voice.play_voice(self.voice.upload_message)


                else:
                    if self.tweet:
                        self.voice.play_voice(self.voice.coming_message)
                    self.ui_queue.put(("NORMAL_MESSAGE",response))




        except Exception as e:

            self.ui_queue.put(("ERROR", f"[red]Error while receiving message: {e}[/red]"))
            self.connection.close()  # type: ignore

    def main(self):

        self.nickname = input("Please enter a nickname: ")
        self.ip_address = "192.168.1.24"
        self.port = 41851
        self.connect_to_server()

        # UI THREAD
        ui_thread = threading.Thread(
            target=self.ui_loop,
            daemon=True
        )
        ui_thread.start()

        # RECEIVE THREAD
        receive_thread = threading.Thread(
            target=self.receive_message,
            daemon=True
        )
        receive_thread.start()

        # SEND THREAD (input)
        send_thread = threading.Thread(
            target=self.send_message
        )
        send_thread.start()

        send_thread.join()


if __name__ == "__main__":
    sender = Sender()
    sender.main()
