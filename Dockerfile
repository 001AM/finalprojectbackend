# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /code/finalbackend

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /code/finalbackend/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK and download required NLTK data
RUN pip install --no-cache-dir nltk && \
    python -m nltk.downloader punkt averaged_perceptron_tagger

# Copy the rest of the application code to the working directory
COPY . /code/finalbackend/

# Install Gunicorn
RUN pip install --no-cache-dir gunicorn

# Expose the ports for WSGI and ASGI
EXPOSE 8000 8001

# Run the application using Gunicorn and Daphne
CMD ["sh", "-c", "gunicorn finalbackend.wsgi:application --reload --bind 0.0.0.0:8000 & daphne -b 0.0.0.0 -p 8001 finalbackend.asgi:application"]
