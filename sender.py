import datetime
import os
import socket
import subprocess
import threading
import time
import webbrowser
from queue import Queue

from rich import print
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from help import Help
from voice_class import Voice
from voice_server import VoiceListen


class Sender:
    def __init__(self) -> None:

        self.ui_queue = Queue()
        self.strtime = datetime.datetime.now()
        self.voice_listen = VoiceListen()
        self.console = Console()
        self.voice_thread_running = False
        self.prompt = (
            "[bold red]<[/bold red][bold green]^[/bold green][bold red]>[/bold red] "
        )
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
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "orange1",
            "orange3",
            "dark_orange",
            "orange_red1",
            "gold1",
            "gold3",
            "gold4",
            "deep_pink1",
            "deep_pink2",
            "deep_pink3",
            "hot_pink",
            "hot_pink2",
            "hot_pink3",
            "violet",
            "violet_red",
            "medium_purple",
            "medium_purple2",
            "blue_violet",
            "dodger_blue1",
            "dodger_blue2",
            "dodger_blue3",
            "sky_blue1",
            "sky_blue2",
            "sky_blue3",
            "spring_green1",
            "spring_green2",
            "spring_green3",
            "sea_green1",
            "sea_green2",
            "sea_green3",
            "turquoise2",
            "turquoise4",
            "dark_turquoise",
            "medium_turquoise",
            "chartreuse1",
            "chartreuse2",
            "chartreuse3",
            "chartreuse4",
            "aquamarine1",
            "aquamarine2",
            "aquamarine3",
            "pale_green1",
            "pale_green3",
            "khaki1",
            "khaki3",
            "khaki4",
            "light_goldenrod1",
            "light_goldenrod3",
            "salmon1",
            "indian_red",
            "orchid",
            "plum1",
            "plum3",
            "slate_blue1",
            "slate_blue3",
            "steel_blue1",
            "steel_blue3",
        ]
        self.voice = Voice()
        self.help = Help()
        self.tweet = True
        self.voice_ip_address = ""
        self.voice_port = 0
        self.print_lock = threading.Lock()

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

    def right_message_panel(self, message, title: str):
        with self.print_lock:
            self.clear_prompt()
            panel = Panel(
                message,
                border_style=self.right_panel_color,
                title=title,
                padding=(0, 2),
                width=30,
            )
            self.console.print(Align.right(panel))

    def center_message_panel(self, message, title="Chat"):
        with self.print_lock:
            self.console.print()
            panel = Panel(
                str(message),
                border_style=self.center_panel_color,
                width=50,
                title=title,
            )
            self.console.print(panel, justify="center")

    def ui_loop(self):
        while True:
            event, data = self.ui_queue.get()

            if event == "ASK_UPLOAD_CONFIRM":
                answer = Prompt.ask(
                    "Please Answer The Question : ( Yes/Or Anything ) ",
                    console=self.console,
                )

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

            elif event == "PRIVATE_UPLOAD_MESSAGE":
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
                self.center_message_panel(data, "Chat")

    def connect_to_server(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.ip_address, self.port))
            # print(f"[green]Connected to server {self.ip_address}:{self.port}[/green]")
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
                    if not self.connection:  # Eğer input beklerken bağlantı koptuysa
                        self.ui_queue.put(
                            ("ERROR", "[red]Bağlantı koptu, işlem yapılamıyor.[/red]")
                        )
                        break  # Döngüden çık
                    self.console.print("\n")
                    # ---------------------------------------------------------------------Active Session------------------------------------------------------------------------------------------
                    if self.active_sessions:
                        if (message.lower() in ["return", "chat"]and self.active_sessions):  # buda Aktif Sesiondan Çıkmak İçin Açan Kişi Kapatıyor Unutma
                            for target in self.active_sessions:
                                self.connection.send(f"EXIT_SESSION {target}".encode(self.encode))
                            self.active_sessions = []  # session temizlenir
                            self.voice.play_voice(self.voice.active_session_exit_message)
                            continue  #

                        if message.startswith("exit") and self.active_sessions:
                            parts = message.split()
                            # 1. Kontrol: Yanında kullanıcı adı var mı?
                            if len(parts) < 2:
                                self.ui_queue.put(("ERROR","[red]Hata: Çıkarmak istediğiniz kullanıcı adını yazın. (Örn: exit ahmet)[/red]",))
                                continue

                            # 2. Değişkeni güvenli bir şekilde al ve temizle
                            target_user = parts[1]
                            target_user = "".join(c for c in target_user if c.isprintable()).strip()

                            # 3. Listede var mı kontrol et ve işlemi yap
                            if target_user in self.active_sessions:
                                self.active_sessions.remove(target_user)
                                self.connection.send(f"REMOVE_USER {target_user}".encode(self.encode) )
                                text = f"Grup görüşmesinden çıkarıldı: {target_user}"
                                self.ui_queue.put(("ACTIVE_SESSION_MESSAGE", text))
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                            else:
                                self.ui_queue.put(("ERROR",f"[yellow]{target_user} aktif oturumda bulunamadı.[/yellow]",))
                            continue  # İşlem bitti, döngünün başına dön (alttaki genel mesaj gönderme kısmına gitme)


                        if message.startswith("PrivateUpload"):
                            if len(message.split()) != 3:
                                text = "FORMAT_ERROR"
                                self.ui_queue.put(("FORMAT_ERROR", text))
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
                                self.true_message.append(f"[green]The file '{file_name}' exists. Sending To Server [The File Size:{size}][/green]")
                                self.connection.send(f"U_START {directory} {file_name} {size}\n".encode(self.encode))  # Dosya Bilgileri Gönderildi
                                with (open(full_path, "rb") as f):  # Dosya Açıldı Okunan Veriler Kontrollu Şekilde Gönderilicek
                                    while True:
                                        chunk = f.read(4096)
                                        if not chunk:
                                            break
                                        self.connection.sendall(chunk)

                                # Mesaj Sağda Gözüksün Diye
                                self.true_message.append(f"[bold green]File '{file_name}' successfully to Send Server [/bold green]")
                                edited_text = Text.from_markup(" ".join(self.true_message), justify="center")  # Metini Editlemek İçin
                                self.ui_queue.put(("PRIVATE_UPLOAD_MESSAGE", edited_text))
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                                self.true_message.clear()

                            except Exception as e:
                                self.false_message.append(f"[red]Upload error:[/red] {e}")
                                edited_text = Text.from_markup(" ".join(self.false_message), justify="center")  # Metini Editlemek İçin
                                self.ui_queue.put(("UPLOAD_MESSAGE", edited_text))
                                self.false_message.clear()
                                continue



                    # -----------------------------------------------------------------Active Session Finished------------------------------------------------------------------------------------------

                    if message.startswith("center_panel_color"):
                        parts = message.split(maxsplit=1)
                        if len(parts) == 2:
                            panel_color = parts[1]
                            if panel_color in self.colors:
                                self.center_panel_color = panel_color
                                text = f"The Panel Color Changed to {panel_color}"
                                self.ui_queue.put(("CHANGED_PANEL_COLOR", text))

                                # --- SESLİ MESAJ BURADA ---
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                                # --------------------------
                            else:
                                text = f"Sorry Unknown Color {panel_color}\nSee All Colors (list_panel_colors)"
                                self.ui_queue.put(("UNKNOW_COLOR", text))
                        else:
                            self.ui_queue.put(("FORMAT_ERROR", "FORMAT ERROR"))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)

                        continue  # Döngünün başına dön

                    elif message.startswith("right_panel_color"):
                        parts = message.split(maxsplit=1)
                        if len(parts) != 2:
                            text = "FORMAT ERROR: Use 'right_panel_color <color>'"
                            self.ui_queue.put(("FORMAT_ERROR", text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        panel_color = parts[1].strip()
                        if panel_color in self.colors:
                            self.right_panel_color = panel_color
                            text = f"The Right Panel Color Changed to {panel_color}"
                            self.ui_queue.put(("CHANGED_PANEL_COLOR", text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                        else:
                            text = f"Sorry Unknown Color: {panel_color}\nSee All Colors with 'list_panel_colors'"
                            self.ui_queue.put(("UNKNOW_COLOR", text))

                        continue

                    elif message.startswith("message_voice"):#Bildirim Sesleri İçin
                        parts = message.split()

                        if len(parts) != 2:
                            self.ui_queue.put(("FORMAT_ERROR","FORMAT ERROR: Use 'message_voice true/false'"))
                            continue

                        bool_value = parts[1].lower()

                        if bool_value == "true":
                            self.tweet = True
                        elif bool_value == "false":
                            self.tweet = False
                        else:
                            self.ui_queue.put(("FORMAT_ERROR", "Only true/false allowed"))
                            continue

                        # 🔊 sadece ayar değiştiyse çal
                        self.voice.play_voice(self.voice.own_message)

                        text = f"Voice notifications set to: {self.tweet}"
                        self.ui_queue.put(("SERVER_MESSAGE", text))
                        continue

                    elif message.startswith("create_voice_chat"):
                        if not self.voice_thread_running:
                            self.voice_thread_running = True

                            threading.Thread(
                                target=self.voice_listen.listen_to_server,
                                args=(self.voice_listen.ip_address, self.voice_listen.port),
                                daemon=True,
                            ).start()

                            self.voice.open_voice()

                        else:
                            self.ui_queue.put(("ERROR", "Voice chat already running"))

                    elif message.startswith("close_voice_chat"):
                        threading.Thread(
                            target=self.voice_listen.exit_the_server, daemon=True
                        ).start()
                        self.voice.close_voice_and_con_err()
                        self.voice_thread_running = False


                    elif message.lower() == "list_panel_colors":
                        text = "()".join(self.colors)
                        self.ui_queue.put(("LIST_PANEL_COLORS", text))
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)

                    elif message.startswith("select"):
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)
                        _, *users = message.split()
                        self.active_sessions = users
                        user_list_str = " ".join(users)
                        self.connection.send(f"SELECTED_USER {user_list_str}".encode())
                        continue

                    elif message[0:6] == "users:":
                        if len(message.split()) <= 2:
                            text = f"FORMAT ERROR"
                            self.ui_queue.put(("FORMAT_ERROR", text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        command, receiver_name, content = message.split(
                            maxsplit=2
                        )  # İl İki Değer Ayrılır Sonraki Deperler Tek Bir Değer Olarka Tutulur
                        full_message = (
                            f"RECEIVER_MESSAGE_NAME {receiver_name} {content}"
                        )
                        self.connection.send(full_message.encode(self.encode))
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)

                        text = "The Message has been sent."
                        self.ui_queue.put(("SENDED_MESSAGE", text))

                    elif message.startswith("users"):
                        full_message = f"GET_USERS {self.nickname}"
                        self.connection.send(full_message.encode())

                    elif message.startswith("cmd"):
                        try:
                            command = message.split(maxsplit=1)[1]  # cmd <komut>
                            process = subprocess.Popen(
                                command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                encoding="latin1",
                            )
                            output, error = (
                                process.communicate()
                            )  # Komut tamamlanana kadar bekle
                            if output:
                                self.ui_queue.put(
                                    (
                                        "SERVER_MESSAGE",
                                        f"[green]Output:[/green]\n{output}",
                                    )
                                )
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                            if error:
                                self.ui_queue.put(
                                    ("ERROR", f"[red]Error:[/red]\n{error}")
                                )
                                if self.tweet:
                                    self.voice.play_voice(self.voice.own_message)
                        except Exception as e:
                            self.ui_queue.put(
                                ("ERROR", f"[red]Command execution error:[/red] {e}")
                            )

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
                            text = "FORMAT_ERROR"
                            self.ui_queue.put(("FORMAT_ERROR", text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            continue

                        try:
                            _, directory, file_name = message.split(" ", 2)
                            full_path = os.path.join(directory, file_name)

                            if not os.path.exists(full_path):
                                self.false_message.append(
                                    "[red]The file does not exist! Please check the path.[/red]"
                                )
                                continue
                            size = os.path.getsize(full_path)
                            self.true_message.append(
                                f"[green]The file '{file_name}' exists. Sending To Server [The File Size:{size}][/green]"
                            )
                            self.connection.send(
                                f"U_START {directory} {file_name} {size}\n".encode(
                                    self.encode
                                )
                            )  # Dosya Bilgileri Gönderildi
                            with (
                                open(full_path, "rb") as f
                            ):  # Dosya Açıldı Okunan Veriler Kontrollu Şekilde Gönderilicek
                                while True:
                                    chunk = f.read(4096)
                                    if not chunk:
                                        break
                                    self.connection.sendall(chunk)

                            # Mesaj Sağda Gözüksün Diye
                            self.true_message.append(
                                f"[bold green]File '{file_name}' successfully to Send Server [/bold green]"
                            )
                            edited_text = Text.from_markup(
                                " ".join(self.true_message), justify="center"
                            )  # Metini Editlemek İçin
                            self.ui_queue.put(("UPLOAD_MESSAGE", edited_text))
                            if self.tweet:
                                self.voice.play_voice(self.voice.own_message)
                            self.true_message.clear()

                        except Exception as e:
                            self.false_message.append(f"[red]Upload error:[/red] {e}")
                            edited_text = Text.from_markup(
                                " ".join(self.false_message), justify="center"
                            )  # Metini Editlemek İçin
                            self.ui_queue.put(("UPLOAD_MESSAGE", edited_text))
                            self.false_message.clear()

                    elif message.lower().strip() in ["exit", "q"]:
                        self.connection.send("exit".encode())
                        self.voice.close_voice_and_con_err()
                        break
                    else:
                        self.connection.sendall(
                            message.encode()
                        )  # Sendall İle Tüm Veri Gönderilir

            except Exception as e:
                self.ui_queue.put(("ERROR", f"[red]Error:[/red]\n{e}"))

        else:
            self.ui_queue.put(
                ("ERROR", "[red]No connection to server. Please connect first.[/red]")
            )

    def receive_message(self):
        if self.connection is None:
            self.ui_queue.put(("ERROR", "[red]Hata: Soket objesi oluşturulamadı.[/red]"))
            return

        while True:
            try:
                response = (self.connection.recv(4096).decode(errors="ignore").strip())

                if not response:
                    self.ui_queue.put(("ERROR", "[red]Server disconnected.[/red]"))
                    self.connection = None  # KRİTİK: Diğer threadlere haber ver
                    break

                if response.startswith("[URL:]"):
                    url = response.split("[URL:]")[1].strip()
                    self.ui_queue.put(("SERVER_MESSAGE", f"Live Stream URL: {url}"))
                    webbrowser.open(url)
                    continue

                if response.startswith("TAKE_USERS_SESSION"):
                    _, user_connections = response.split(" ", 1)
                    self.active_sessions = [
                        user.strip() for user in user_connections.split("/")
                    ]
                    self.voice.play_voice(self.voice.active_session_message)
                    continue

                if response.startswith("TAKE_USERS"):
                    _, user_list = response.split(" ", 1)
                    user_list = "".join(
                        c for c in user_list if c.isprintable()
                    ).strip()
                    self.ui_queue.put(("TAKE_USERS", user_list))
                    if self.tweet:
                        self.voice.play_voice(self.voice.own_message)
                    continue

                if response.startswith("TAKE_SPECIAL_MESSAGE"):
                    _, special_message = response.split(" ", 1)
                    message = special_message.strip()
                    self.ui_queue.put(("TAKE_SPECIAL_MESSAGE", message))
                    continue

                if response.startswith("UPLOAD_MESSAGE"):
                    _, question = response.split(maxsplit=1)
                    message = "".join(c for c in question if c.isprintable()).strip()
                    self.ui_queue.put(("UPLOAD_MESSAGE", message))
                    self.ui_queue.put(("ASK_UPLOAD_CONFIRM", None))
                    continue

                if response.startswith("UPLOAD_FILE"):
                    _, file_name = response.split(" ", 1)
                    self.file_obj = open(file_name, "wb")
                    self.connection.send(b"ready")
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
                    continue # Döngü başına dön

                else:
                    if response:
                        self.ui_queue.put(("NORMAL_MESSAGE", response))
                        if self.tweet:
                            self.voice.play_voice(self.voice.own_message)

            except (ConnectionResetError, ConnectionAbortedError):
                self.ui_queue.put(("ERROR", "[red]Bağlantı koptu. Lütfen yeniden bağlanın.[/red]"))
                if self.connection:
                    try:
                        self.connection.close()
                    except:
                        pass
                self.connection = None
                break  # ARTIK HATA VERMEZ: Çünkü while True içindeki try-except'teyiz.

            except Exception as e:
                # Beklenmedik diğer hatalar için
                self.ui_queue.put(("ERROR", f"[red]Bilinmeyen Hata: {e}[/red]"))
                break

    def main(self):

        self.nickname = input("Please enter a nickname: ")
        self.ip_address = "192.168.1.24"
        self.port = 41851
        self.connect_to_server()

        # UI THREAD
        ui_thread = threading.Thread(target=self.ui_loop, daemon=True)
        ui_thread.start()

        # RECEIVE THREAD
        receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        receive_thread.start()

        # SEND THREAD (input)
        send_thread = threading.Thread(target=self.send_message)
        send_thread.start()

        send_thread.join()


if __name__ == "__main__":
    sender = Sender()
    sender.main()
