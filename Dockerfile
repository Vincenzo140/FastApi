FROM python:3.11

WORKDIR /app
COPY requirements/ requirements
 
RUN pip install -r requirements/requirements.txt

# COPY . .

CMD ["python", "src/main.py"]