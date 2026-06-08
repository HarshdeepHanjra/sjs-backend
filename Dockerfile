# Use the official Python 3.11 image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files to disk and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 10000 available to the world outside the container (Render uses this port by default)
EXPOSE 10000

# Run the application with gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:10000"]