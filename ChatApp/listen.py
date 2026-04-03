import socket
import threading
from rich import print
from datetime import datetime
import random
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.columns import Columns
import time


class Listener:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.clients = {}  # keys = connection || values = user_name
        self.log_file = "log_file.txt"
        self.encode = "utf-8"
        self.users_color = {}  # keys = username || values == colors
        self.colors = [
        "red", "green", "yellow",
        "blue", "magenta", "cyan", "white",  "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta",
        "bright_cyan","orange1", "orange3", "dark_orange", "orange_red1", "gold1", "gold3", "gold4",
        "deep_pink1", "deep_pink2", "deep_pink3", "hot_pink", "hot_pink2", "hot_pink3",
        "violet", "violet_red", "medium_purple", "medium_purple2", "blue_violet",
        "dodger_blue1", "dodger_blue2", "dodger_blue3", "sky_blue1", "sky_blue2", "sky_blue3",
        "spring_green1", "spring_green2", "spring_green3", "sea_green1", "sea_green2", "sea_green3",
        "turquoise2", "turquoise4", "dark_turquoise", "medium_turquoise",
        "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4",
        "aquamarine1", "aquamarine2", "aquamarine3","pale_green1", "pale_green3",
        "khaki1", "khaki3", "khaki4", "light_goldenrod1", "light_goldenrod3",
        "salmon1","indian_red", "orchid", "plum1", "plum3",
        "slate_blue1", "slate_blue3", "steel_blue1", "steel_blue3"
                       ]
        self.prompt = ""
        self.console = Console()
        self.selected_user_session = {}
        self.upload_data = b""
        self.directory = ""
        self.file_name = ""
        self.general_panel_color = "light_sky_blue1"
        self.special_message_panel_color = "medium_purple3"

    def assign_color(self, nickname):
        if nickname not in self.users_color:
            self.users_color[nickname] = random.choice(self.colors)

    def log_message(self, message):
        with open(self.log_file, "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {message}\n")

    def broadcast(self, message, sender_connection=None):

        for other_connection in list(self.clients.keys()):
            if other_connection != sender_connection:  # Gönderen hariç
                try:
                    other_connection.send(message.encode(self.encode))
                    time.sleep(0.01) # 3️ Küçük bir bekleme (Rich panel çıktısı, renkli yazılar veya hızlı mesajlaşma için)
                except Exception as e:
                    error_user = self.clients.get(other_connection, "Unknown")
                    self.console.print(f"[red]Broadcast error to {error_user}:[/red] {e}")
                    # 5️ Hatalı bağlantıyı güvenli şekilde kapat
                    self.disconnect_client(other_connection)


    def handle_client(self, connection, address):
        # Aşağıda Bağlatı İsteği ve Bilgileri Gönderildi
        #
        #
        #
        try:
            nickname = connection.recv(1024).decode().strip()#İlk İsim Bilgisi Geliyor

            if nickname in self.clients.values():
                connection.send("[red]Nickname already taken. Please try again.[/red]".encode())
                connection.close()
                return
   

            with self.lock: 
                self.clients[connection] = nickname
           
            self.assign_color(nickname)
            join_message = f"[{self.users_color[nickname]}]{nickname} has joined the chat.[/]"

            self.log_message(join_message)
            self.broadcast(f"{join_message}", connection)  
            panel1 = Panel(f"[green]{nickname} : [white]Connected From[/white] [blink]{address[0]}:{address[1]}[/blink] [/green]",title="", subtitle="", border_style="white")
            self.console.print(panel1)



            while True:
                response_message = connection.recv(4096).decode().strip()
                if not response_message:
                    break
                if response_message.startswith("GET_USERS"):  # Kullanıcı listesini istemek için komut
                    try:
                        _, user_info = response_message.split()  # User bilgisini al
                        for connect, user_name in self.clients.items():
                            if user_name == user_info:
                                user_list = ' / '.join(self.clients.values())
                                connection.send(f"TAKE_USERS {user_list}".encode())
                        continue  # <---- Bu çok önemli! Döngü altına düşmesini engeller
                    except ValueError:
                        connection.send("Invalid GET_USERS format. Use: GET_USERS <username>".encode())
                    continue

                if response_message.startswith("EXIT_SESSION"):
                    _, target_user = response_message.split(maxsplit=1)
                    # Eğer bu connection session'daysa, session’ı kapat
                    if connection in self.selected_user_session:
                        del self.selected_user_session[connection]
                        connection.send(f"TAKE_SPECIAL_MESSAGE You have exited private session with {target_user}".encode(self.encode))
                    continue

                if response_message.startswith("REMOVE_USER"):
                    _, target_user = response_message.split(maxsplit=1)
                    if connection in self.selected_user_session:
                        for conn in self.selected_user_session[connection][:]:  # [:] Bu Şekilde Sonuna Listenin[:] koyarsan Liste Kopyalanır
                            if self.clients.get(conn) == target_user:
                                self.selected_user_session[connection].remove(conn)

                        connection.send(f"TAKE_SPECIAL_MESSAGE {target_user} The User Not In Group Chat Anymore.".encode())

                if response_message.startswith("SELECTED_USER"):
                    try:
                        _, user_info = response_message.split(" ", 1) #Gelen Mesajı Ayırdık dizi halinde her indexse değişken atadık
                        user_names = user_info.split()  # birden fazla kullanıcı [Ahmet , Serap]
                        target_connections = []

                        for name in user_names:
                            for conn, client_name in self.clients.items():
                                if client_name.lower() == name.lower() and conn not in target_connections:
                                    target_connections.append(conn)
                                    break

                        if target_connections:
                            self.selected_user_session[connection] = target_connections
                            #Burada Self Nesnesinin İçine Aktif Olan Kullancıyı Atadık Sonra Kullanmak İçin
                            connection.send(f"TAKE_USERS_SESSION {' / '.join(user_names)}".encode(self.encode))
                            # Yasir / Talha /reyyan Şeklinde Gidicek
                        else:
                            connection.send(f"ERROR UserNotFound {user_info}".encode(self.encode))
                    except Exception as e:
                        print(f"[red]Error handling SELECTED_USER: {e}[/red]")
                if response_message.startswith("RECEIVER_MESSAGE_NAME"): #
                    try:
                        _, target_name, content = response_message.split(maxsplit=2)
                        sender_name = self.clients.get(connection, "Unknown")
                        full_message = f"[red]{sender_name}:[/red] {content}"
                        for conn, name in self.clients.items():
                            if name == target_name:
                                conn.send(f"TAKE_SPECIAL_MESSAGE {full_message}".encode(self.encode))
                                break
                    except Exception as e:
                        print("Error sending special message:", e)
                    continue   #Bu Alan Hame Özel Mesaj İletimini Hemde Özel Açılan Bağlatıda ki Mesajları İletiyor Sender.py İçerisnde Gelen Mesaj İşlenip Ekrana Basılıyor



                if response_message.startswith(f"U_START"):
                    self.upload_data = b""
                    self.file_name = ""
                    self.directory = ""
                    _,directory,file_name ,file_size = response_message.split(maxsplit=3)#İlk Mesaj Ayrıldı Gerek Varmı Bilmiyom Ama Ayırdım
                    self.directory = directory
                    self.file_name = file_name
                    remaining_data = int(file_size)
                    time.sleep(0.1)#100ms
                    full_message = f"UPLOAD_MESSAGE[{self.users_color[nickname]}]{nickname}[/]: Do You Want To  Take File ?  ( Yes / OR Anything )"
                    self.broadcast(full_message, connection)

                    while remaining_data > 0:
                        chunk = connection.recv(min(4096, remaining_data))
                        if not chunk:
                            break
                        self.upload_data += chunk
                        remaining_data -= len(chunk)


                        type_m = f"Received {len(self.upload_data)} bytes of {file_name}"
                        message = Panel(f"[green]{type_m} : [white]Connected From[/white] [blink]{address[0]}:{address[1]} [/green]",title="", subtitle="", border_style="white")
                        print(message)
                if response_message.startswith("Yes"):
                    type_m = f"Data Ready For Sending ..."
                    message = Panel(f"[green]{type_m} : [white]Connected From[/white] [blink]{address[0]}:{address[1]} [/green]")
                    print(message)

                    connection.send(f"UPLOAD_FILE {self.file_name}".encode())
                    ack = connection.recv(16).decode(errors="ignore")
                    if ack.strip().lower() != "ready": # ready Gelmez İSe Veriler Gitmez
                        continue  # istemci hazır değilse atla

                    for i in range(0, len(self.upload_data), 4096):
                        part = self.upload_data[i:i + 4096]
                        connection.send(part)

                    connection.send(b"END")



                    # sadece özel session'ı kapat
                    if connection in self.selected_user_session: ## Eğer Özel Session AKtif İse Server Tarafından Kapanıcak
                        del self.selected_user_session[connection]

                    continue  # döngü devam etsin, connection kapanmasın



                # Normal mesaj iletimi
                full_message = f"[{self.users_color[nickname]}]{nickname}[/]: {response_message}"
                self.log_message(full_message)
                # Eğer bu connection bir private session içindeyse
                if connection in self.selected_user_session:
                    sender_name = self.clients[connection]
                    full_message = f"{sender_name}: {response_message}"
                    for target_conn in self.selected_user_session[connection]:  # Listeyi döngü ile gönder
                        try:
                            target_conn.send(f"TAKE_SPECIAL_MESSAGE {full_message}".encode(self.encode))
                        except Exception as e:
                            print(f"[red]Error sending to {self.clients.get(target_conn, 'Unknown')}:[/red] {e}")

                else:
                    # Normal broadcast
                    full_message = f"[{self.users_color[nickname]}]{nickname}[/]: {response_message}"
                    self.broadcast(full_message, connection)





        except Exception as e:
            panel1 = Panel(f"[red]Error handling client {address}:[/red] {e}", style="red")
            self.console.print(panel1)
        finally:
            if connection in self.clients:  # eğer bağlantı listenin içinde varsa sonlandır s
                self.disconnect_client(connection)








    def listen_for_connections(self, ip_address, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((ip_address, port))
                sock.listen()
                panel1 = Panel("[blink][white]Server is listening for connections...[/white][/blink]", title="",subtitle="", border_style="green")
                self.console.print(panel1)

                while True:
                    connection, address = sock.accept()
                    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) #Bu Paketlerin Anında gönderilmesini Sağlar
                    threading.Thread(target=self.handle_client, args=(connection, address)).start()

        except Exception as e:
            print(f"[red]Server Error:[/red] {e}")

    def disconnect_client(self, connection):
        if connection not in self.clients:  # çift silme koruması
            return

        nickname = self.clients.get(connection, "Unknown User")
        if nickname:
            leave_message = f"{nickname} : Has Left The Chat!!"
            message = Panel(leave_message, style="red")
            self.log_message(leave_message)
            self.console.print(message)
            with self.lock:
                del self.clients[connection]
            connection.close()
            self.broadcast(f"[yellow]{leave_message}[/yellow]", connection)
            user_count = len(self.clients)
            message = Panel(f"[dim]Active users: {user_count}[/dim]",title="", subtitle="", border_style="white")
            self.console.print(message)


    def main(self):

        ip = "0.0.0.0" 
        port = 10601
        self.listen_for_connections(ip, port)


if __name__ == "__main__":
    listen = Listener()
    listen.main()
