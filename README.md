# BookSpider

采用scrapy-redis爬去京东图书，当当图书和Amazon图书，采用分布式爬虫爬取数据，实现爬虫的暂停和开始，断点再续，URL去重，数据存储等，属于轻量级爬虫。适合刚入手的朋友们了解学习。欢迎大家一起交流沟通学习。

Python交流群：942913325


### 安装Python

至少Python3.5以上

### 安装Redis

安装好之后将Redis服务开启

### 配置redis服务

```
cd book
```

进入book目录，修改settings.py文件

修改REDIS_URL 

格式为REDIS_URL = 'redis://[:password@]127.0.0.1:6379'

[：password@] :为redis密码，如无则不填


#### 运行爬虫

```
python main.py
```


## 项目参考

本项目代码来自黑马工程师资教学12天培训课，如需资源，加群了解更多！