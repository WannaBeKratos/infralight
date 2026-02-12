FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy project metadata first for better layer caching
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the project
RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "-m", "infralight.main"]
