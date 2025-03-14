FROM python:3.10

WORKDIR /app
COPY . /app

# Upgrade pip & wheel to avoid outdated dependency resolution
RUN pip install --upgrade pip wheel setuptools  

RUN pip install -r requirements.txt  

CMD ["python", "bot.py"]
