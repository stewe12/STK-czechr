FROM python:3.8-slim

WORKDIR /app

COPY stk_czechr/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY stk_czechr/ .

CMD ["python", "fetch_car_inspection.py"]
