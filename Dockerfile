FROM python:3.13.3

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "run.py"]