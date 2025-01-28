FROM python:3.11-slim

# Install PortAudio development library
RUN apt-get update && apt-get install -y portaudio19-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy and run your application
COPY . .
CMD ["python", "app.py"]
