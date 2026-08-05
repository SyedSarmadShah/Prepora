FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements directory
COPY requirements/ /app/requirements/

# Install python dependencies
RUN pip install --no-cache-dir -r requirements/development.txt

# Copy backend codebase
COPY . /app/

# Expose Django port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/admin/ || exit 1

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
