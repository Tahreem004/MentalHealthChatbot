# Use a lightweight Python image
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install ffmpeg and required tools
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    apt-get clean

# Set work directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependenciess
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Railway will use
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
