# 使用官方 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置时区为 UTC（pytz 会转换成巴西时间）
ENV TZ=UTC

# 创建工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制全部代码
COPY . .

# 运行 Bot
CMD ["python", "jili.py"]
