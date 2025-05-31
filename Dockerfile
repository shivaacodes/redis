# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your app
COPY . .

# Install dependencies
RUN pip install fastapi[all] redis httpx

# Expose the FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
