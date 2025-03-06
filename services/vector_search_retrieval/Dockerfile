# Choose a Base Image
FROM python:3.12.8-slim

# Set the Working Directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the service runs on (if it has an API)
EXPOSE 5000

# Set the command to run the service
CMD ["python", "vector_search_service.py"]
