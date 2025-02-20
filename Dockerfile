# Start with Python Alpine base
FROM python:3.11-alpine

# Install Chrome and other dependencies
RUN apk upgrade --no-cache --available \
    && apk add --no-cache \
      chromium \
      chromium-chromedriver \
      chromium-swiftshader \
      ttf-freefont \
      font-noto-emoji \
      bash \
    && apk add --no-cache \
      --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community \
      font-wqy-zenhei

# Set Chrome environment variables
ENV CHROME_BIN=/usr/bin/chromium-browser \
    CHROME_PATH=/usr/lib/chromium/ \
    CHROMIUM_FLAGS="--disable-software-rasterizer --disable-dev-shm-usage"

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables for the app
ENV PORT=8080
ENV WEBSITES_PORT=8080

# Create a non-root user and set permissions
RUN adduser -D appuser \
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
