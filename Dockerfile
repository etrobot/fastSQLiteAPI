FROM python:3.10-slim

WORKDIR /app

# 安装 poetry
RUN pip install poetry

# 复制项目文件
COPY pyproject.toml poetry.lock ./
COPY app ./app

# 配置 poetry 不创建虚拟环境
RUN poetry config virtualenvs.create false

# 安装依赖
RUN poetry install --no-dev

# 创建数据目录
RUN mkdir -p /app/data

# 运行应用
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"] 