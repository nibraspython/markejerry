FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip wheel setuptools  

# Install tgcalls first to avoid dependency conflicts
RUN pip install tgcalls==0.0.16  
RUN pip install -r requirements.txt  

CMD ["python", "bot.py"]
