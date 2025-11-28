FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app

# Copy entire project (respecting .dockerignore)
COPY . .

# Install from requirements file
RUN python -m pip install --no-cache-dir -r requirements.txt

# Set AWS region environment variable
ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1

# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Install OpenTelemetry
RUN python -m pip install aws_opentelemetry_distro_genai_beta>=0.1.2
ENV OTEL_SDK_DISABLED=true

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 8080

CMD ["opentelemetry-instrument", "python", "-m", "handler"]
