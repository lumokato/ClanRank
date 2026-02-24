FROM python:3.10.16-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /app/

RUN adduser --disabled-password --no-create-home appuser
USER appuser

WORKDIR /

EXPOSE 8000

CMD ["python", "/app/main.py"]

