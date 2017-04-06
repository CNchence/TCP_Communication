
# telnet program example
import socket,sys
import threading

class Getmessage(threading.Thread):
    def __init__(self,s,lock):
        threading.Thread.__init__(self)
        self.s = s
        self.lock =lock
    def run(self):
        while 1:
            try:
                self.data = s.recv(1024)
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
                self.data = input(' ')
                s.send(self.data.encode('utf8'))
            except:
                sys.exit()



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



