FROM python:3.8

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ./script/get_count.py ./ 



CMD ["python", "./script/get_count.py"]
