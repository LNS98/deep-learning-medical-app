FROM python:3.7
WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip install --upgrade -r requirements.txt
COPY . .
CMD ["python", "api.py"]

#RUN apk add --no-cache gcc musl-dev linux-headers
