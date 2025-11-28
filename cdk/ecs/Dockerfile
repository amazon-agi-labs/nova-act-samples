FROM public.ecr.aws/docker/library/python:3.12-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies as root
RUN playwright install-deps chromium

# Set AWS region environment variables
ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1

# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Set Nova Act API key
# ENV NOVA_ACT_API_KEY=<placeholder>

# Skip Playwright installation check since we install it manually
ENV NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL=true

# Copy application code
COPY app.py .

# Create non-root user
RUN useradd -m -u 1000 nova_act_user
USER nova_act_user

# Install Playwright browsers as the non-root user
RUN playwright install chromium

CMD ["python", "app.py"]
