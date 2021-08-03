FROM python:alpine
WORKDIR /app

# Prevent Python from creating compiled bytecode and
# writing messages to stdout as we won't have access to them
# anyway
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["./run.sh"]
