FROM node:20
RUN npm install -g eslint 
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --break-system-packages fastapi uvicorn python-multipart
COPY ../eslint.config.js /app/eslint.config.js
COPY ../runner.py /app/runner.py
WORKDIR /app
EXPOSE 5000
CMD ["uvicorn", "runner:app", "--host", "0.0.0.0", "--port", "5000"]