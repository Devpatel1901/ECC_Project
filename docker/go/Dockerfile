FROM golang:1.22
RUN go install golang.org/x/lint/golint@latest && \
    apt-get update && apt-get install -y python3-pip 
RUN pip3 install --break-system-packages fastapi uvicorn python-multipart
ENV PATH="/go/bin:$PATH"
COPY ../runner.py /app/runner.py
WORKDIR /app
EXPOSE 5000
CMD ["uvicorn", "runner:app", "--host", "0.0.0.0", "--port", "5000"]