# TCP通信
客户端使用库 socket,sys,threading
服务器端使用库 socket,select,threading

# mysql
客户端开始使用用户注册登录机制，服务器端使用mysql数据库记录用户登录信息，因此想要运行服务器端程序，需要修改mysql数据库信息

# 使用注意
1.客户端mysql服务器参数应按照本地数据库修改
2.服务器，客户端host,port需要匹配

# 已知BUG
input阻塞问题，究其原因，还是因为没有界面导致输入框只有一个......无法分辨用户输入是要说的话，还是发送给服务器的指令
直接影响是 发送端在发出“发送文件给xxxx”后，需要输入任意字符退出发送消息的input   文件接收端在选择文件保存地址时 需要输入两次

talking is cheap