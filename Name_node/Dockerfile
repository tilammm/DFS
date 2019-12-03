# python:latest looks like debian jessie with latest python3 installed
FROM python:latest

# install nc to test out the socketserver with some TCP packets!
RUN apt-get update && apt-get install -y netcat-openbsd

ADD . /nn
COPY requirements.txt /nn
WORKDIR /nn

RUN pip install -r requirements.txt
# CMD ["ls", "-al"]
CMD ["python3", "name_node.py"]
