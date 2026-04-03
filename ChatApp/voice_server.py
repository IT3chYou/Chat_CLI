import socket
import threading
from rich import print
from rich.console import Console
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align


class VoiceListen:

    def __init__(self) -> None:
        self.ip_address = "127.0.0.1"
        self.port = 9999
        self.connection = None
        self.clients = set()   # sadece addr tutacağız
        self.voice_server_info = ""
        self.console = Console()
        self.special_message_panel_color = "medium_purple3"

    def broadcast_to_client(self, sender_addr, data):
        try:
            for addr in list(self.clients):
                if addr != sender_addr:
                    self.connection.sendto(data, addr)
        except Exception as e:
            print("[red]Error:[/red]", e)

    def listen_to_server(self, ip_address, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.bind((ip_address, port))
        self.connection.settimeout(1.0)
        print()
        text = f"Dear User Voice Server Has Been Planted\n [green]Listening UDP {ip_address}:{port}[/green]"
        panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Voice Server Info",padding=(0, 2), width=30)
        self.console.print(panel, justify="right")
        

        while True:
            try:
                self.thread_handle_the_server()
            except socket.timeout:
                continue



    def thread_handle_the_server(self):
        thread = threading.Thread(target=self.handle_to_server,daemon=True)
        thread.start()
        return thread


    def handle_to_server(self):
        data, addr = self.connection.recvfrom(4096)

        if addr not in self.clients:
            self.clients.add(addr)
            print()
            text = f"[cyan]Voice client joined {addr}[/cyan]"
            panel = Panel(Text.from_markup(text, justify="center"),border_style=self.special_message_panel_color, title=f"Voice Server Info",padding=(0, 2), width=30)
            self.console.print(panel, justify="right")
            return

        # SESİ AYNEN İLET – decode / encode YOK
        self.broadcast_to_client(addr, data)




    def exit_the_server(self):
        try:
            if self.connection:
                self.connection.close()

            self.clients.clear()

            print()
            text = "[cyan]The Server Has Been Closed By You. See You Admin[/cyan]"
            panel = Panel(
                Text.from_markup(text, justify="center"),
                border_style=self.special_message_panel_color,
                title="Voice Server Info",
                padding=(0, 2),
                width=30
            )
            self.console.print(panel, justify="right")

        except Exception as e:
            print("[red]Error while closing server:[/red]", e)


