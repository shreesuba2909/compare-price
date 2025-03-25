# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the necessary directories
RUN mkdir -p /app/frontend

# Copy the rest of the application code into the container
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run"]