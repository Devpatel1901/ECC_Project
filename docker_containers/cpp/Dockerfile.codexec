FROM gcc:latest
WORKDIR /code
COPY runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
