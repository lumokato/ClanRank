FROM python:3.10.16-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

# 安全: 非 root 用户运行
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["python", "app.py"]

