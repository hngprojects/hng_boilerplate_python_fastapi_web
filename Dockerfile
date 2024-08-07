# Use an official Python runtime as the base image
FROM python:3.11.9-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy the rest of the backend files
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]
