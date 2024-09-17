# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app code
COPY . /app

# Expose port 8080
EXPOSE 8080

# Command to run the FastAPI app with uvicorn
CMD ["uvicorn", "routes:app", "--host", "0.0.0.0", "--port", "8080"]