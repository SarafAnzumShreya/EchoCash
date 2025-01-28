# Use the official Python 3.11 image as a base
FROM python:3.11-slim

# Install dependencies (including portaudio)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean

# Set up your working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 5000

# Start the Flask application
CMD ["python", "app.py"]
