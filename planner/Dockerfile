FROM python:3.12-alpine
RUN apk add --no-cache tzdata
WORKDIR /app
COPY server.py index.html VERSION /app/
COPY icons /app/icons
CMD ["python3", "-u", "/app/server.py"]
