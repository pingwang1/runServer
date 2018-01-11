import time
from MyWebServer import HttpServer

ROOT_HOME = "./html"
def get_time(env,start_response):
	statu = "200 ok"
	headers = [("Content-Type", "text/html; charset=utf-8")]
	start_response(statu, headers)
	return time.ctime()

def get_hello(env,start_response):
	statu = "200 ok"
	headers = [("Content-Type", "text/html; charset=utf-8")]
	start_response(statu, headers)
	return "hello!"

class Application(object):
	def __init__(self,urls):
		self.urls = urls

	def __call__(self,env,start_response):
		# env = {
		# 	"PATH_INFO": file_name,
		# 	"METHOD": method
		# }
		file_name = env.get("PATH_INFO","/")
		print("file_name:%s"%file_name)

		# if file_name.startswith("/static"):
		if file_name.endswith(".html") or file_name.endswith(".js"):
			# name = file_name[7:]
			name = file_name[:]
			try:
				f = open(ROOT_HOME+name,"r")
			except:
				statu = "404 Not Found"
				headers = [("Content-Type", "text/html; charset=utf-8")]
				start_response(statu, headers)
				return "文件找不到！哈哈"
			else:
				content = f.read()
				statu = "200 ok"
				headers = [("Content-Type", "text/html; charset=utf-8")]
				start_response(statu, headers)
				return content
		#遍历urls
		for url,function in urls:
			if file_name ==url:
				response_body = function(env,start_response)
				return response_body
		#找不到的情况
		statu = "404 Not Found"
		headers = [("Content-Type", "text/html; charset=utf-8")]
		start_response(statu,headers)
		return "文件找不到！哈哈"

urls = [
		("/ctime",get_time),
		("/hello",get_hello)
	]
app = Application(urls)
#
# if __name__ == "__main__":
# 路由配置
# 	urls = [
# 		("/ctime",get_time),
# 		("/hello",get_hello)
# 	]
# 	app = Application(urls)
# 	# 执行app()时就会执行__call__
# 	http_server = HttpServer(app)
# 	http_server.bind(8081)
# 	http_server.start()


