
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from rich.align import Align
from rich.columns import Columns



class Help:
    def __init__(self):
        self.console = Console()

    def show_help(self):
        """Rich ile güzel görünümlü help paneli gösterir."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")

        commands = [
            ("help", "For Help Menu."),
            ("exit / q", "Exit The Application."),
            ("cls", "Clear The Console (Windows: cls, Unix: clear)."),
            ("list_panel_colors", "That Command Will Show You All Supported Colors For Change To Panel's Colors. "),
            ("panel_color <color>", "That Command Changed The Special Message Panel Color"),
            ("users", "The Command Take Active Users From The Server ."),
            ("users: <receiver> <message>", "Message To USer: Example; users: Ahmet Merhaba"),
            ("select <k1> <k2> ...",
             "Bir veya birden fazla kullanıcıyla özel/çoklu oturum başlatma talebi gönderir."),
            ("exit <users>", "Sunucuya özel oturumdan çıkış bildirir (istemci exit ile de tetiklenir)."),
            ("cmd <komut>", "Yerel makinede komut çalıştırır (Windows: cmd, Unix: bash)."),
            ("start_video_screen", "Start a Video Recorder With HTTP Protocols"),
            ("stop_video_screen", "That Command Will Stop Video Screen"),
            ("upload <file_path> <file_name>", "How To Upload File to General Chat")

        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        footer = Text.assemble(("Not: ", "bold yellow"),
                               ("The execution of commands depends on the server’s protocol. Pay attention to the special message",
                                "white"))
        panel = Panel.fit(Align.center(table), title="[bold green]Commands — Help[/bold green]",
                          border_style="bright_blue", padding=(1, 2))

        # Konsola yazdır
        self.console.print(panel)
        self.console.print(Panel(footer, border_style="yellow", padding=(0, 1)))


