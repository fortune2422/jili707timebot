# 使用官方 Python 3.10 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --upgrade pip && pip install -r requirements.txt

# 暴露端口（FastAPI 用）
EXPOSE 10000

# 启动命令
CMD ["python", "jili.py"]
