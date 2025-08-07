# 使用官方 Python 3.10 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制所有项目文件到容器中
COPY . .

# 安装依赖
RUN pip install --upgrade pip && pip install -r requirements.txt

# 启动命令
CMD ["python", "jili.py"]
