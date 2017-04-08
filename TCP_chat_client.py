import socket,sys
import threading
import File_Send_Server_Class as FileServer
import File_Send_Client_Class as FileClient


class Getmessage(threading.Thread):
    def __init__(self,s,lock):
        threading.Thread.__init__(self)
        self.s = s
        self.lock =lock
    def run(self):
        global threadlist
        while 1:
            try:
                self.data = s.recv(1024)
                if self.data.decode('utf8') == "god_code:文件发送端":

                    self.lock.acquire()
                    path = input("输入待发送文件的路径(比如:d:\\test.txt):")
                    self.lock.release()

                    self.data = s.recv(1024)
                    getuser = self.data.decode('utf8')
                    host,port = getuser.split(' ')
                    print(host,port)
                    t3 = File_client_threading(host,int(port)+10,path)
                    threadlist.append(t3)
                    t3.start()
                elif self.data.decode('utf8') == "god_code:文件接收端":
                    socketname = self.s.getsockname()
                    host = str(socketname[0])
                    port = str(socketname[1])
                    print(host,port)
                    t4 = File_server_threading(host, int(port)+10)
                    threadlist.append(t4)
                    t4.start()
                else :
                    print(self.data.decode('utf8'))

            except:
                sys.exit()



class Sendmessage(threading.Thread):
    def __init__(self,s,lock):
        threading.Thread.__init__(self)
        self.s = s
        self.lock = lock
    def run(self):
        while 1 :
            try:
                self.lock.acquire()
                self.data = input(' ')
                self.lock.release()
                s.send(self.data.encode('utf8'))
            except:
                sys.exit()
#############################################文件_服务器类  接收端####################################################
class File_server_threading(threading.Thread,FileServer.File_server):
    def __init__(self,host,port):
        FileServer.File_server.__init__(self,host,port)
        threading.Thread.__init__(self)
    def run(self):
        self.recv_file()
########################################################################################################################
###########################################文件_用户类_发送端###########################################################
class File_client_threading(threading.Thread,FileClient.File_client):
    def __init__(self,host,port,path):
        FileClient.File_client.__init__(self,host,port,path)
        threading.Thread.__init__(self)
    def run(self):
        self.send_file()
########################################################################################################################

# main function
if __name__ == "__main__":

    host = "127.0.0.1"
    port = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #s.settimeout(2)
    threadlist = []
    lock = threading.Lock()
    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print('无法连接服务器')
        sys.exit()

    print('已连接服务器，可以通信')


    t1 = Getmessage(s,lock)
    threadlist.append(t1)
    t2 = Sendmessage(s,lock)
    threadlist.append(t2)
    t1.start()
    t2.start()

    for t in threadlist:
        t.join()

    print("连接已断开")



