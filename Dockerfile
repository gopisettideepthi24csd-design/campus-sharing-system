# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose port 8000
EXPOSE 8000

# Set the working directory to backend for running the app
WORKDIR /app/backend

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
