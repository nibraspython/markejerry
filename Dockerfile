FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip setuptools wheel

# Install tgcalls first to avoid conflicts
RUN pip install tgcalls==2.0.0

# Install all other dependencies
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
