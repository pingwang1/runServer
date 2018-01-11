#conding=utf-8
from multiprocessing import Process
from socket import *
import re
import sys
import subprocess
import json

ROOT_HOME = "./html"

class HttpServer(object):
	def __init__(self,app):
		self.server = socket(AF_INET, SOCK_STREAM)
		self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.app = app

	def bind(self,port):
		self.server.bind(("", port))

	def start(self):
		self.server.listen(128)
		while True:
			new_socket, new_address = self.server.accept()
			print("新用户：%s连接了" % str(new_address))
			Process(target=self.recvAndSend, args=(new_socket, new_address)).start()
			new_socket.close()

	def start_response(self,statu,headers):
		start_line = "HTTP/1.1 "+statu+"\r\n"
		start_headers =""
		for header in headers:
			start_headers += "%s:%s\r\n"%header
		self.response_headers = start_line + start_headers

	def recvAndSend(self,new_socket, new_address):
		recv_data = new_socket.recv(1024)
		print("%s:\n%s" % (str(new_address), recv_data.decode("utf-8")))
		print("debug1==%s"%recv_data.decode("utf-8"))
		request_data1 = recv_data.decode("utf-8").splitlines()[0]
		print("debug2==%s"%request_data1)
		if request_data1.startswith("POST"):
			#获取要执行的代码块
			# response_data =recv_data.decode("utf-8").splitlines()[11:]
			# print("debug3==%s" % response_data)
			# f = open("test.py", "w")
			# for data in response_data:
			# 	print("debug4==%s"%data)
			# 	f.write(data+"\n")
			# f.close()

			#利用正则切割收到客户端发来的代码块（取\n\n后的内容）
			print("没处理前的数据%s"%recv_data.decode("utf-8"))
			response_data = re.search(r"(\r\n){2,}((.|\s)+)",recv_data.decode("utf-8")).group(2)
			print("debug3==%s" % response_data)
			f = open("test.py", "w")
			f.write(response_data)
			f.close()
			#执行发过来的代码（网上找的代码）使用python3执行的代码
			obj = subprocess.Popen(["python3"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
								   universal_newlines=True)
			f = open("test.py", "r")
			content = f.read()
			out_error_list = obj.communicate(content)
			#返回结果是一个元组，元组的０是程序的返回结果，１是执行代码的错误信息提示
			print("返回的结果：%s"%str(out_error_list))
			print(out_error_list[0])
			if not out_error_list[0]:
				result = "请检查输入的代码正确性，谢谢！"
				print("bug")
			else:
				result = out_error_list[0]
			# origin = "http://192.168.16.57:8080"
			origin = "http://localhost:8080"
			re_data = "HTTP/1.1 200 ok\r\n" +"Content-Type:text/html; charset=utf-8\r\nAccess-Control-Allow-origin: "+origin+"\r\n"+"\r\n"+str(result)
			new_socket.send(re_data.encode("utf-8"))
		else:
			# 主要是需要处理发送过来的数据中的请求行
			request_data = recv_data.decode("utf-8").splitlines()[0]
			print("debug")
			file = re.match(r"(\w+)\s(.+)\s.+", request_data)
			file_name = file.group(2)
			# print("debug3==%s" % file_name)
			method = file.group(1)
			env = {
				"PATH_INFO": file_name,
				"METHOD": method
			}
			response_body = self.app(env, self.start_response)
			self.response_data = self.response_headers + "\r\n" + response_body
			# print("debug4==%s"%self.response_data)
			new_socket.send(self.response_data.encode("utf-8"))

		new_socket.close()
if __name__ == "__main__":
	# 执行app()时就会执行__call__
	sys.path.insert(0,ROOT_HOME)
	argvs = sys.argv[1]
	module_name,module_app = argvs.split(":")
	# print(module_name)
	# print(module_app)
	m = __import__(module_name)
	#获得类
	app = getattr(m,module_app)
	http_server = HttpServer(app)
	http_server.bind(8080)
	http_server.start()