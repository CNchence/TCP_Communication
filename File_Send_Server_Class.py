import socket
import hashlib
import struct
import threading
import queue
import math

'''
file_queue = queue.Queue()
class Write_File(threading.Thread):
    def __init__(self, file_path, file_frequency):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.file_frequency = int(file_frequency)
        self.cycle_num = 0
    def run(self):
        global file_queue
        with open(self.file_path, 'wb') as fw:
            while self.cycle_num < self.file_frequency:
                try:
                    fw.write(file_queue.get())
                    time.sleep(0.001)
                    self.cycle_num += 1
                except:
                    continue'''



class File_server():
    def __init__(self, host, port):
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
        global file_queue
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                        #修改为AF_INET就为ipv4通信
            server_address = (self.HOST, self.PORT)
            sock.bind(server_address)
            sock.listen(1)
            print("用户向你发送文件，等待连接")
            client_socket, client_address = sock.accept()
            print("%s 连接成功" % str(client_address))

            file_info_package = client_socket.recv(self.info_size)
            self.unpack_file_info(file_info_package)
            print("文件名：",self.filename.decode('utf8'),"文件大小：",self.file_size)

            '''
            file_frequency = float(self.file_size)/ float(self.BUFFER_SIZE)             #计算需要写入的次数
            file_frequency = math.ceil(file_frequency)
            print(file_frequency)'''

            recved_size = 0
            #self.PATH = input("输入保存地址(比如c:\桌面\):")
            self.PATH = "f:\\"                             #注意 此处是接受文件的保存地址，在某些电脑上多线程配合不好，有可能导致崩溃，因此使用固定保存地址，当然也可以尝试自行输入的方式，当也要在程序运行时输入两次
            client_socket.send("ok".encode('utf8'))
            with open(self.PATH+self.filename.decode('utf8'),'wb') as fw:
                while recved_size < self.file_size:
                    recv_file = client_socket.recv(self.BUFFER_SIZE)
                    recved_size += len(recv_file)
                    #此处直接用每一帧收到的数据长度加到总长度上，而不是用之前的buffer_size！因为在传输过程中，每一帧都不一定是满帧！！
                    fw.write(recv_file)


            save_md5 = self.cal_md5()
            if save_md5 != self.md5.decode('utf8'):
                print(save_md5)
                print(self.md5.decode('utf8'))
                print('MD5 验证错误')
            else:
                print("接收成功")

        except socket.errno:
            print("Socket error")
        finally:
            print("传输完毕")
            sock.close()



if __name__ == "__main__":
    hostname = socket.gethostname()
    #ip = socket.gethostbyname(hostname)
    #print("本机局域网ip地址为：",ip)
    PORT_input = input("输入服务器端口：")
    a = File_server('2001:da8:8002:31f4::2:bef1',int(PORT_input))
    a.recv_file()