FROM openjdk:21-slim
RUN apt-get update && apt-get install -y wget curl unzip python3-pip && \
    wget -O /checkstyle.jar https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.12.3/checkstyle-10.12.3-all.jar && \
    wget -O /google_checks.xml https://raw.githubusercontent.com/checkstyle/checkstyle/master/src/main/resources/google_checks.xml
RUN pip3 install --break-system-packages fastapi uvicorn python-multipart
COPY ../runner.py /app/runner.py
WORKDIR /app
EXPOSE 5000
CMD ["uvicorn", "runner:app", "--host", "0.0.0.0", "--port", "5000"]