
import socket, select
import threading
import pymysql   #提示找不到pymysql.connect时，使用anaconda 安装库     #anaconda命令行输入conda install pymysql


class NewClient(threading.Thread):                              #专用于新用户创建名字时，等待用的  避免新用户输入名字是阻塞主循环
    def __init__(self,sock,addr):
        threading.Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.samename = 0

    def init_mysql(self):                                                #数据库初始化并连接
        self.connection = pymysql.connect(host='127.0.0.1',
                                     port=3306,
                                     user='root',
                                     password='chencemysql',
                                     db='python_chat',
                                     charset='utf8mb4')
        self.cursor = self.connection.cursor()

    def run(self):
        '''
        global Namelist
        global CONNECTION_LIST
        print("Client (%s, %s) connected" % self.addr)                      #与用户通信 获取名字
        self.sock.send("请输入你的名字：".encode('utf8'))
        name = self.sock.recv(RECV_BUFFER)
        while True:
            for key in Namelist.keys():
                if Namelist[key] == name.decode('utf8'):               #检查是否有重名的客户端
                    self.sock.send("聊天室已有该名字用户，请重新输入".encode('utf8'))
                    name = self.sock.recv(RECV_BUFFER)
                    self.samename = 1
                    break
            if self.samename == 1 :
                self.samename = 0
                continue
            else:
                break
        Namelist[self.sock] = name.decode('utf8')
        broadcast_data(self.sock, "%s 进入房间\n" % name.decode('utf8'))   #通知已在线的用户，新用户的加入'''
        global Namelist
        global CONNECTION_LIST
        self.init_mysql()                                                   #建立数据库连接
        print("Client (%s, %s) connected" % self.addr)

        self.sock.send("欢迎连接,请输入你的用户名：".encode('utf8'))     #请用户输入用户名 并查找数据库 是否存在
        username = self.sock.recv(RECV_BUFFER)

        sql = "select name,password from user where username = \"%s\""  # 查询数据
        data = (username.decode('utf8'))
        if self.cursor.execute(sql % data) == 0 :                                  #如果不存在，引导用户新建
            self.sock.send("输入的用户名不存在，请新建用户".encode('utf8'))
            self.sock.send("输入密码".encode('utf8'))
            password = self.sock.recv(RECV_BUFFER)
            self.sock.send("请输入你的昵称：".encode('utf8'))
            name = self.sock.recv(RECV_BUFFER)

            while True:                                                         #待修改  应该为查找数据库 昵称 看是否有重复
                for key in Namelist.keys():
                    if Namelist[key] == name.decode('utf8'):               #检查是否有重名的客户端
                        self.sock.send("聊天室已有该名字用户，请重新输入".encode('utf8'))
                        name = self.sock.recv(RECV_BUFFER)
                        self.samename = 1
                        break
                if self.samename == 1 :
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
            self.sock.send("输入密码".encode('utf8'))
            while True:
                password = self.sock.recv(RECV_BUFFER)
                if password.decode('utf8') == mysql_password:
                    break
                self.sock.send("密码错误，请重新输入:".encode('utf8'))
            name = mysql_name.encode('utf8')
            Namelist[self.sock] = name.decode('utf8')


        broadcast_data(self.sock, "%s 进入房间\n" % name.decode('utf8'))   #通知已在线的用户，新用户的加入





        self.connection.commit()                                         #数据库连接关闭
        self.cursor.close()
        self.connection.close()






def broadcast_data (sock, message):                                       #定义广播函数，将文字发给除了说话人以及主线程的其他人
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


if __name__ == "__main__":


    CONNECTION_LIST = []                                                              #用于记录已连接人的socket
    RECV_BUFFER = 4096
    PORT = 5000                                                                       #端口号

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                 #建立socket服务器 开始监听
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", PORT))                                           #服务器IP
    server_socket.listen(10)

    CONNECTION_LIST.append(server_socket)                                              #将服务器socket加入连接列表

    print("Chat server started on port " + str(PORT))

    Namelist = {}

    while 1:
        read_sockets ,write_sockets ,error_sockets = select.select(CONNECTION_LIST ,[] ,[])
        #通过select函数选出所有read请求的socket
        #print("要处理的请求有",len(read_sockets))
        for sock in read_sockets:                                                        #对有read请求的socket进行处理
            if sock == server_socket:                                  #如果是服务器socket的请求，那就是有新的用户接入
                sockfd, addr = server_socket.accept()
                t = NewClient(sockfd, addr)
                t.start()
                CONNECTION_LIST.append(sockfd)
                #print('新加入一个用户')

            else:
                try:
                    data = sock.recv(RECV_BUFFER)                       #如果不是服务器socket  就将他说的话广播
                    data = data.decode('utf8')
                    #print(data)
                    if data:
                        broadcast_data(sock, "\r" + '<' + Namelist[sock] + '> ' + data)
                except:
                    broadcast_data(sock, "用户 %s 断开连接" % Namelist[sock])             #出现异常 说明该用户已经断开连接
                    print("Client (%s, %s) is offline" % addr)
                    sock.close()
                    CONNECTION_LIST.remove(sock)                                         #清除该用户的socket列表数据 以及字典数据
                    Namelist.pop(sock)
                    continue

    server_socket.close()

