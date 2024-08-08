# Use an official Python runtime as the base image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

#copy the requirements.txt file and install with pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the backend files
COPY . /app/

# Expose the port the app runs on
EXPOSE 7001

# Command to run the application
CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 7001 --reload"]