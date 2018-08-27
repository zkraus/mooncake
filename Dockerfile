FROM fedora-minimal:latest
RUN microdnf install -y python pip
RUN mkdir mooncake
WORKDIR /mooncake
ADD main.py /mooncake
COPY mooncake/ /mooncake/mooncake
ADD requirements.txt /mooncake
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
