import socket
import hashlib
import struct

class File_server():
    def __init__(self,host,port):
        self.HOST = host
        self.PORT = port
        self.BUFFER_SIZE = 1024
        self.HEAD_STRUCT = '128sIq32s'
        self.info_size = struct.calcsize(self.HEAD_STRUCT)

    def cal_md5(self):
        with open(self.PATH + self.filename.decode('utf8'),'rb') as fr:
            md5 = hashlib.md5()
            md5.update(fr.read())
            md5 = md5.hexdigest()
            return md5

    def unpack_file_info(self,file_info):
        self.filename,self.file_name_len,self.file_size,self.md5 = struct.unpack(self.HEAD_STRUCT,file_info)
        self.filename = self.filename[:self.file_name_len]

    def recv_file(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.HOST, self.PORT)
            sock.bind(server_address)
            sock.listen(1)
            print("等待连接")
            client_socket, client_address = sock.accept()
            print("%s 连接成功" % str(client_address))

            file_info_package = client_socket.recv(self.info_size)
            self.unpack_file_info(file_info_package)
            print("文件名：",self.filename.decode('utf8'),"文件大小：",self.file_size)

            recved_size = 0
            self.PATH = input("输入保存地址(比如c:\桌面\):")
            client_socket.send("ok".encode('utf8'))
            with open(self.PATH+self.filename.decode('utf8'),'wb') as fw:
                while recved_size < self.file_size:
                    remained_size = self.file_size - recved_size
                    recv_size = self.BUFFER_SIZE if remained_size > self.BUFFER_SIZE else remained_size
                    recv_file = client_socket.recv(recv_size)
                    recved_size += recv_size
                    fw.write(recv_file)
            save_md5 = self.cal_md5()
            if save_md5 != self.md5.decode('utf8'):
                print('MD5 验证错误')
            else:
                print("接收成功")

        except socket.errno:
            print("Socket error")
        finally:
            sock.close()



if __name__ == "__main__":
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print("本机局域网ip地址为：",ip)
    PORT_input = input("输入服务器端口：")
    a = File_server(ip,int(PORT_input))
    a.recv_file()

