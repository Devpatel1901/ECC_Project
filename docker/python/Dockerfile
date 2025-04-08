FROM python:3.11-slim
RUN pip install fastapi uvicorn pylint python-multipart
COPY ../runner.py /app/runner.py
WORKDIR /app
EXPOSE 5000
CMD ["uvicorn", "runner:app", "--host", "0.0.0.0", "--port", "5000"]