from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

def downloadVideo(url,filename):
	response =requests.get(url,stream=True)
	response.raise_for_status()
	with open(filename,"wb") as file:
		for chunk in response.iter_content(chunk_size=8192):
			if chunk:
				file.write(chunk)
				
class Video(BaseModel):
    videoId: str
    videoUrl: str

# 因为是抖音发起的，所以需要要把抖音的这个地址加进去    
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://www.douyin.com",
    "https://www.douyin.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
