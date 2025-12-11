FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt . 

RUN pip install -r requirements.txt

COPY app.py .

COPY templates/ templates/

ENV PORT=8000

CMD ["python", "app.py"] 

