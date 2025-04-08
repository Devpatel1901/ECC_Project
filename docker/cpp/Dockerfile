FROM gcc:13
RUN apt-get update && apt-get install -y python3 python3-pip cppcheck
RUN pip3 install --break-system-packages fastapi uvicorn python-multipart
COPY ../runner.py /app/runner.py
WORKDIR /app
EXPOSE 5000
CMD ["python3", "-m", "uvicorn", "runner:app", "--host", "0.0.0.0", "--port", "5000"]
