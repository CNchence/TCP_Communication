
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
    '''
    while 1:

        rlist = [s]

        # Get the list sockets which are readable
        read_list, write_list, error_list = select.select(rlist , [], [])

        for sock in read_list:
            # incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    # print data
                    sys.stdout.write(data.decode('utf8'))
                    prompt()

                if data == "saying":
                    msg = sys.stdin.readline()
                    s.send(msg.encode('utf8'))
                    prompt()'''


            # user entered a message



