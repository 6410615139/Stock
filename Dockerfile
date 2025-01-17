# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y libjpeg-dev zlib1g-dev && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Command to run the init script
CMD ["bash", "-c", "./init.sh"]
