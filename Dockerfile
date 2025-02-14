FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables for Azure Container Apps
ENV PORT=8080
ENV WEBSITES_PORT=8080

# Create a non-root user and switch to it
RUN useradd -m -s /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the port the app runs on
EXPOSE 8080

# Copy application code
COPY webdriver_client.py .
COPY scraper.py .
COPY tasks.py .
COPY main.py .

# Command to run the application
CMD ["python", "main.py"]

