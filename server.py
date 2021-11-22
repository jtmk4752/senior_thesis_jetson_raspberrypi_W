import socket
import threading
from datetime import datetime
import RPi.GPIO as GPIO
import time
import subprocess

HOST_IP = "192.168.200.2" # サーバーのIPアドレス
PORT = 9979 # 使用するポート
CLIENTNUM = 3 # クライアントの接続上限数
DATESIZE = 1024 # 受信データバイト数
pin = 27

class SocketServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # サーバー起動 
    def run_server(self):

        # server_socketインスタンスを生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(CLIENTNUM)
            print('[{}] run server'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            while True:
                # クライアントからの接続要求受け入れ
                client_socket, address = server_socket.accept()
                print('[{0}] connect client -> address : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), address) )
                client_socket.settimeout(60)
                # クライアントごとにThread起動 send/recvのやり取りをする
                t = threading.Thread(target = self.conn_client, args = (client_socket,address))
                t.setDaemon(True)
                t.start()
    
    def sound(self, switch):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin,GPIO.OUT,initial=GPIO.LOW)
        p = GPIO.PWM(pin,1)
        p.start(50)

        if switch == True:
            p.ChangeFrequency(622.254)
            time.sleep(0.8)
            p.stop()
            time.sleep(0.1)

        else:
            p.ChangeFrequency(493.9)
            time.sleep(0.1)
            p.ChangeFrequency(196)
            time.sleep(0.6)
            p.stop()
            time.sleep(1)

        GPIO.cleanup()


    # クライアントごとにThread起動する関数
    def conn_client(self, client_socket, address):
        
        with client_socket:
            while True:
                # クライアントからデータ受信
                rcv_data = client_socket.recv(DATESIZE)
                if rcv_data :
                    if rcv_data.decode('utf-8') == "1000000":
                        client_socket.send(rcv_data)
                        self.sound(True) #USB connected
                        print('[{0}] recv date : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rcv_data.decode('utf-8')) )
                    else:
                        client_socket.send(rcv_data)
                        self.sound(False) #USB disconnected
                        print('[{0}] recv date : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rcv_data.decode('utf-8')) )                        
                else:
                    break

        print('[{0}] disconnect client -> address : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), address) )

if __name__ == "__main__":
    cmd = subprocess.Popen(["raspivid -t 0 -w 1024 -h 768 -fps 5 -b 2000000 -awb auto -n -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=0.0.0.0 port=8554"],shell=True)
    SocketServer(HOST_IP, PORT).run_server()