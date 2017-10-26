Docker for Flask
==================== 

### Dockerfile
```
FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip
WORKDIR /app
COPY ./ /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
```


### Build 
```sh
docker build -t flask .
```

### Run
```sh
docker run --name flask -v $PWD/:/app/ -it -d -p 5000:5000 flask app.py
```
