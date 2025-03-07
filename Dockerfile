FROM python:3.11-slim

# Install Chrome and other dependencies
RUN apt-get update
RUN apt-get install -y \
      chromium \
      chromium-driver \
      bash
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables for the app
ENV PORT=8080
ENV WEBSITES_PORT=8080

# Set Chrome environment variables
ENV CHROME_BIN=/usr/bin/chromium \
    CHROME_PATH=/usr/lib/chromium/
#    CHROMIUM_FLAGS="--disable-software-rasterizer --disable-dev-shm-usage"

# Create a non-root user and set permissions
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

# Copy application code
COPY webdriver_client.py .
COPY scraper.py .
COPY tasks.py .
COPY main.py .

# Expose ports (if needed)
EXPOSE 8080

# Update the Chrome path in the Python code
ENV CHROME_BINARY=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Command to run the application
CMD ["python", "main.py"]
