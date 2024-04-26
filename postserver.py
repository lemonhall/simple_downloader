from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
#这是为了给popup.html里面的视频查看器可以查看而用http方式server所有的mp4文件,所需要引用的包
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlparse
import requests

import os

app = FastAPI()

#这是为了给popup.html里面的视频查看器可以查看而用http方式server所有的mp4文件的一个方法
app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.post("/videos")身后具体的下载以及剪贴板使用逻辑
def downloadVideo(url,filename):
	response =requests.get(url,stream=True)
	response.raise_for_status()
    # 修改存储路径为 static 子文件夹
	static_path = os.path.join('static', filename)

	with open(static_path,"wb") as file:
		for chunk in response.iter_content(chunk_size=8192):
			if chunk:
				file.write(chunk)
	#把刚才下载好的文件拷贝到剪贴板，这里比较特殊的地方就是利用了wsl2和windows共享文件访问的特性
    #另外还利用了powershell的特性，这里又利用了wsl2下可以无缝得调用windows的应用程序的特性
	#稍微恶心一点的就是\转义被转来转去的，这里可以打开一个powershell测试，如果成功复制，直接粘贴
    #powershell下回车就会直接调用默认绑定的app，比如vlc去打开这个文件，经过测试，成功复制到微信
	#不用自动调用微信了，虽然也就是用js调用url-scheme的事情，weixin://这样的，但有点复杂了，算了
    #本来就是alt-tab然后ctrl+v的事情
	path = '\\\\wsl.localhost\\Ubuntu-22.04\\home\\lemonhall\\douyin\\static\\'+filename
	print(path)
	command = f"powershell.exe Set-Clipboard -LiteralPath \"\\\\{path}\""
	print(command)
	os.system(command)
				


# 因为是抖音发起的，所以需要要把抖音的这个地址加进去
# 后面那个是为了让popup.html可以cors访问我们的python接口的    
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://www.douyin.com",
    "https://www.douyin.com",
    "http://localhost",
    "http://localhost:8080",
	"chrome-extension://ddkhdgbdpfkckkfjghhgpgaiomdimmko",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoPath(BaseModel):
    src: str
	
# 删除视频的代码
@app.post("/delete_video")
async def delete_video(videoPath: VideoPath):
    # 在这里添加删除视频的逻辑
	parsed_url = urlparse(videoPath.src)
	video_filesystem_path = "."+parsed_url.path
	print(f"要删除的视频源: {video_filesystem_path}")
	try:
		os.remove(video_filesystem_path)
		print("视频文件删除成功")
	except FileNotFoundError:
		print("文件未找到")
	except Exception as e:
		print("删除文件时发生错误:", e)
	return {"message": "视频删除成功"}


# 这个是popup.html会调用的方法，具体其实是在popup.js里面调用的
# 返回的其实就是一堆形如http://localhost:8000/static/xxxx.mp4的文件列表而已
# 前端会for循环组装一个个的video元素，并将以上Url填入video元素的src属性，即可
@app.post("/list_mp4_files")
async def list_mp4_files():
    base_path = 'http://localhost:8000/'
    mp4_files = [base_path + os.path.join('static/', file) for file in os.listdir('static/') if file.endswith('.mp4')]
    return {"mp4_files": mp4_files}


class Video(BaseModel):
    videoId: str
    videoUrl: str
	

# content.js监听o键，然后把video的id发给了background.js，然后由它发起xhr的post请求
# 请求的执行内容也简单，就是下载文件，并且把对应的文件用powershell的技巧发送的剪切板去
# 方便后续复制粘贴分享
@app.post("/videos")
async def main(video: Video):
	downloadVideo(video.videoUrl,video.videoId+".mp4")
	return video

#用这个去启动
#建立环境
#python3 -m venv .venv
#激活环境
#source .venv/bin/activate
#服务启动
#uvicorn postserver:app --reload
#安装依赖
#pip install fastapi fastapi-cors uvicorn requests
#可能的一个bug
#不知道是不是误删了还是怎么了，长期运行，然后之间.venv不见了，可能是误删了，不管了
