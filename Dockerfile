# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip wheel setuptools  

# Install tgcalls first to avoid dependency conflicts
RUN pip install tgcalls>=3.0.0.dev5

# Install all dependencies
RUN pip install -r requirements.txt  

# Run bot
CMD ["python", "bot.py"]
