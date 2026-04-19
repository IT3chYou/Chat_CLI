import socket
import threading
from rich import print
import socket
import pyaudio


class Sender:
    def __init__(self) -> None:
        self.ip_address = ""
        self.port = 0
        self.connection = None
        self.nickname = "Guest"
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channel = 1
        self.rate = 44100
        self.audio = pyaudio.PyAudio()


    def connect_to_server(self, ip_address:str, port:int):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.connect((ip_address, port))
        self.connection.settimeout(1.0)
        print("[green]UDP ready[/green]")
        
    #Bağlatı Sağlandı Aynı Zamanda Bağlanan Kşinin İsmi Gidicek


    def send_voice(self):
        
        stream_in = self.audio.open(input=True,format=self.format,channels=self.channel,rate=self.rate,frames_per_buffer=self.chunk)
        

        try:
            while True:
                data = stream_in.read(self.chunk, exception_on_overflow=False)
                self.connection.send(data)
        except Exception as e:
            print("Error : " , e)

    
    def receive_voice(self):
        stream_out = self.audio.open(
            output=True,
            format=self.format,
            channels=self.channel,
            rate=self.rate,
            frames_per_buffer=self.chunk
        )

        self.connection.settimeout(1.0)

        while True:
            try:
                data = self.connection.recv(4096)
                stream_out.write(data)

            except socket.timeout:
                continue

            except Exception as e:
                print("Voice receive error:", e)
                break





if __name__ == "__main__":
    ip_address = str(input(" Please Enter Voice Server Ipv4 Address : "))
    port_number = int(input("Please Enter Voice Server Port : "))
    sender = Sender()
    sender.connect_to_server(ip_address,port_number)

    

    threading.Thread(
        target=sender.send_voice,
        daemon=False
    ).start()

    threading.Thread(
    target=sender.receive_voice,
    daemon=False
    ).start()
