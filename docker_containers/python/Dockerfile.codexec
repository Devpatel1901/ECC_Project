FROM python:3.12-slim
WORKDIR /code
COPY runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
