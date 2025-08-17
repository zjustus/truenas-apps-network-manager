FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir docker
COPY main.py /app/
CMD ["python", "main.py"]