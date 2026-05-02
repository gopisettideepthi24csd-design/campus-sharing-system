# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory to /app
WORKDIR /app

# Copy the entire project
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose port 8000
EXPOSE 8000

# Change to backend directory and run uvicorn
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
