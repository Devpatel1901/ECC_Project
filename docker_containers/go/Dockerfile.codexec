FROM golang:1.21
WORKDIR /code
COPY runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
