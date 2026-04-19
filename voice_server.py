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
        self.running = False
        self.ip_address = "127.0.0.1"
        self.port = 9999
        self.connection = None
        self.clients = set()   # sadece addr tutacağız
        self.voice_server_info = ""
        self.console = Console()
        self.special_message_panel_color = "medium_purple3"



    def listen_to_server(self, ip_address, port):
        self.running = True

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.bind((ip_address, port))
        self.connection.settimeout(1.0)

        text = f"Voice Server Running\n[green]UDP {ip_address}:{port}[/green]"
        panel = Panel(Text.from_markup(text), border_style=self.special_message_panel_color)
        self.console.print(panel, justify="right")

        while self.running:
            try:
                data, addr = self.connection.recvfrom(4096)

                if addr not in self.clients:
                    self.clients.add(addr)
                    self.console.print(f"[cyan]Voice client joined {addr}[/cyan]")

                for client in list(self.clients):
                    if client != addr:
                        try:
                            self.connection.sendto(data, client)
                        except:
                            self.clients.discard(client)

            except socket.timeout:
                continue

            except OSError:
                break   # socket kapandıysa çık



    def exit_the_server(self):
            try:
                self.running = False

                if self.connection:
                    try:
                        self.connection.shutdown(socket.SHUT_RDWR)
                    except Exception as e:
                        print("Error:",e)
                    self.connection.close()
                    self.connection = None

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
                print(e)
