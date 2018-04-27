#服务器IP和端口号：98，103行
#mysql服务器修改
import socket, select
import threading
import pymysql   #提示找不到pymysql.connect时，使用anaconda 安装库     #anaconda命令行输入conda install pymysql
import re
import subprocess                  #用于自动寻找本机IPv6地址

class NewClient(threading.Thread):                              #专用于新用户创建名字时，等待用的  避免新用户输入名字是阻塞主循环
    def __init__(self, sock, addr):
        threading.Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.samename = 0

    def init_mysql(self):                                                #数据库初始化并连接
        self.connection = pymysql.connect(host='127.0.0.1',                     #mysql数据库参数，使用之前请修改
                                     port=3306,
                                     user='root',
                                     password='chencemysql',
                                     db='python_chat',
                                     charset='utf8mb4')
        self.cursor = self.connection.cursor()

    def run(self):
        global Namelist
        global CONNECTION_LIST
        self.init_mysql()                                                   #建立数据库连接
        print("Client (%s, %s, %s, %s) connected" % self.addr)              #注意，ipv6的addr是4个数据组成   如果要改为ipv4，addr只有两位  所以要去掉两个%s
        #print("Client (%s, %s) connected" % self.addr)                     #ipv4

        self.sock.send("Welcome, please enter your username".encode('utf8'))     #请用户输入用户名 并查找数据库 是否存在
        username = self.sock.recv(RECV_BUFFER)

        sql = "select name,password from user where username = \"%s\""  # 查询数据
        data = (username.decode('utf8'))
        if self.cursor.execute(sql % data) == 0:                                  #如果不存在，引导用户新建
            self.sock.send("Username does not exist,please create a new user".encode('utf8'))
            self.sock.send("Enter password".encode('utf8'))
            password = self.sock.recv(RECV_BUFFER)
            self.sock.send("Please enter your nickname:".encode('utf8'))
            name = self.sock.recv(RECV_BUFFER)

            sql = "select name from user "  # #查找数据库 昵称 看是否有重复
            self.cursor.execute(sql)
            namelist = self.cursor.fetchall()

            while True:
                for row in namelist:
                    if row[0] == name.decode('utf8'):               #检查是否有重名的客户端
                        self.sock.send("The nickname already exists, please re-enter".encode('utf8'))
                        name = self.sock.recv(RECV_BUFFER)
                        self.samename = 1
                        break
                if self.samename == 1:
                    self.samename = 0
                    continue
                else:
                    break
            Namelist[self.sock] = name.decode('utf8')
            sql = "insert into user (name,username,password)values(\"%s\",\"%s\",\"%s\")"
            data = (name.decode('utf8'), username.decode('utf8'), password.decode('utf8'))
            self.cursor.execute(sql % data)
        else:
            userdata = self.cursor.fetchall()                                     #查找到数据库存在该用户名  引导用户登陆
            mysql_name = userdata[0][0]
            mysql_password = userdata[0][1]
            self.sock.send("Enter password".encode('utf8'))
            while True:
                password = self.sock.recv(RECV_BUFFER)
                if password.decode('utf8') == mysql_password:
                    break
                self.sock.send("Wrong password, please re-enter".encode('utf8'))
            name = mysql_name.encode('utf8')
            Namelist[self.sock] = name.decode('utf8')

        self.sock.send("You have entered the chat room".encode('utf8'))
        broadcast_data(self.sock, "%s enters the room\n" % name.decode('utf8'))   #通知已在线的用户，新用户的加入
        self.connection.commit()  # 数据库连接关闭
        self.cursor.close()
        self.connection.close()



def broadcast_data (sock, message):                                       #定义广播函数，将文字发给除了说话人以及服务器以外的其他人
    for socket in CONNECTION_LIST :
        if socket != server_socket and socket != sock and socket in Namelist.keys():
            try :
                socket.send(message.encode('utf8'))
                #print("发送成功",message)
            except :
                #print("发送失败")
                socket.close()
                CONNECTION_LIST.remove(socket)
                Namelist.pop(sock)

def get_host_ip():                 #use connect to google ipv6 dns to get self ipv6 ip address
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(('2001:4860:4860::8888', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

if __name__ == "__main__":

    CONNECTION_LIST = []                                                              #用于记录已连接人的socket
    RECV_BUFFER = 1024
    PORT = 5000                                                                       #服务器端口号，使用之前请修改

    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)                 #建立socket服务器 开始监听  修改为AF_INET就为IPV4
    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                  # IPV4
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                 #操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口

    iPv6_address = get_host_ip()
    print("Server ipv6 address", iPv6_address)

    server_socket.bind((iPv6_address, PORT))
    #server_socket.bind(("127.0.0.1", PORT))                                                            # 服务器IP,使用之前请修改  ipv4
    server_socket.listen(10)
    File_Send_re = re.compile("send file to (.*)")
    CONNECTION_LIST.append(server_socket)                                              #将服务器socket加入连接列表

    print("Chat server started on port " + str(PORT))

    Namelist = {}

    while 1:
        read_sockets ,write_sockets ,error_sockets = select.select(CONNECTION_LIST ,[] ,[])
        #通过select函数选出所有read请求的socket
        #print("要处理的请求有",len(read_sockets))
        for sock in read_sockets:                                                        #对有read请求的socket进行处理
            try:                                                           #当用户连接但是没有登陆就断开时，会报错
                if sock == server_socket:                                  #如果是服务器socket的请求，那就是有新的用户接入
                    sockfd, addr = server_socket.accept()
                    #print(sockfd)
                    t = NewClient(sockfd, addr)
                    t.start()
                    CONNECTION_LIST.append(sockfd)
                    #print('新加入一个用户')

                else:
                    try:
                        FindClient = False
                        data = sock.recv(RECV_BUFFER)                       #如果不是服务器socket  就将他说的话广播
                        data = data.decode('utf8')
                        #print(data)
                        '''
                        if data:
                            broadcast_data(sock, "\r" + '<' + Namelist[sock] + '> ' + data)'''

                        if File_Send_re.match(data) :
                            mat = File_Send_re.match(data)
                            file_need = mat.group(1)
                            file_need = file_need.strip()

                            for key in Namelist.keys():
                                if Namelist[key] == file_need:
                                    File_Sock_Need = key
                                    FindClient = True
                                    break
                            if FindClient :
                                sock.send("god_code:File sender".encode('utf8'))
                                File_Sock_Need.send("god_code:File receiver".encode('utf8'))
                                File_Sock_Need_peername = File_Sock_Need.getpeername()
                                sock.send(str(File_Sock_Need_peername[0]+" "+str(File_Sock_Need_peername[1])).encode('utf8'))
                            else :
                                sock.send((mat.group(1)+" does not exist or is not online").encode('utf8'))

                        else :
                            broadcast_data(sock, "\r" + '<' + Namelist[sock] + '> ' + data)


                    except:
                        broadcast_data(sock, "%s disconnect" % Namelist[sock])             #出现异常 说明该用户已经断开连接
                        print("Client (%s, %s, %s, %s) is offline" % addr)                    #ipv6
                        #print("Client (%s, %s) is offline" % addr)                            # ipv4
                        sock.close()
                        CONNECTION_LIST.remove(sock)                                         #清除该用户的socket列表数据 以及字典数据
                        Namelist.pop(sock)
                        continue
            except:
                CONNECTION_LIST.remove(sock)
                print("Did not land and left")

    server_socket.close()

