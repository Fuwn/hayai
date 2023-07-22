FROM python:3.11-alpine

WORKDIR /hayai

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "hayai", "run", "--host=0.0.0.0"]
