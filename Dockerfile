# 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制应用程序的文件到容器中
COPY . /app

# 安装 Flask 和其他依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量，URL 前缀可以在运行容器时通过 -e 来覆盖
ENV IMAGE_URL_PREFIX=https://image.95pter.com/

# 暴露 Flask 默认端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 启动 Flask 应用
CMD ["flask", "run"]
