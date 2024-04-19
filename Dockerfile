FROM python:3.10.6
RUN mkdir /opt/mycode
COPY ./python_file_name  /opt/mycode/python_file_name
RUN pip install -r /opt/mycode/python_file_name/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
WORKDIR /opt/mycode
CMD python main.py

