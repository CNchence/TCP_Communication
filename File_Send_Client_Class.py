import socket
import os
import hashlib
import struct
class File_client():
    def __init__(self,host,port,path):
        self.HOST = host
        self.PORT = port
        self.PATH = path
        self.BUFFER_SIZE = 1024
        self.HEAD_STRUCT = '128sIq32s'

    def cal_md5(self):
        with open(self.PATH,'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def get_file_info(self):
        self.file_name = os.path.basename(self.PATH)
        self.file_name_len = len(self.file_name.encode('utf8'))
        self.file_size = os.path.getsize(self.PATH)
        self.md5 = self.cal_md5()

    def send_file(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.HOST,self.PORT)
        self.get_file_info()                              #创建代传输文件的信息
        print('文件名：', self.file_name, '文件大小：', self.file_size, 'md5校验码：', self.md5)
        file_head = struct.pack(self.HEAD_STRUCT, self.file_name.encode('utf8'), self.file_name_len, self.file_size,
                                self.md5.encode('utf8'))  # 将文件信息装载在一个结构中
        try:
            sock.connect(server_address)
            sock.send(file_head)
            sent_size = 0
            print("等待对方确认")
            enable_send = sock.recv(self.BUFFER_SIZE)
            print("开始传输")
            print("waiting...")

            with open(self.PATH,'rb') as fr:
                while sent_size < self.file_size:
                    remained_size = self.file_size - sent_size
                    send_size = self.BUFFER_SIZE if remained_size > self.BUFFER_SIZE else remained_size
                    send_file = fr.read(send_size)
                    sent_size += send_size
                    sock.send(send_file)
                print("传输完毕，关闭连接")
        except:
            print("无法连接")
        finally:
            sock.close()


if __name__ == "__main__":
    file_host = input("输入传输目标IP:")
    file_port = input("输入目标端口号:")
    file_addr = input("输入代传文件地址:")
    a = File_client(file_host,int(file_port),file_addr)
    a.send_file()

