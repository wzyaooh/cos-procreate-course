# 匿名使用统计服务：只用 Python 标准库，数据存在 /data/stats.db
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN mkdir -p /data && chown 65534:65534 /data && python selftest.py >/dev/null
USER 65534
ENV STATS_DB=/data/stats.db PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "app.py"]
