FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

# Update dependencies
RUN apt-get update && \
    apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev

ARG LAMBDA_DIR="/lambda"

# Lambda directory
RUN mkdir -p ${LAMBDA_DIR}
COPY app.py ${LAMBDA_DIR}

# Install packages
RUN pip install --target ${LAMBDA_DIR} awslambdaric nova-act

WORKDIR ${LAMBDA_DIR}

# Set SDK environment variables for Lambda runtime
ENV NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL=1
ENV NOVA_ACT_BROWSER_ARGS="--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process"
# Use system Playwright browsers instead of /opt/playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "app.handler" ]
