# ------------------------------
# Habit Tracker App - Dockerfile
# ------------------------------

# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Copy dependency list first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Run tests automatically (optional — can be removed)
RUN pytest -v || true

# Define the default command for the CLI app
ENTRYPOINT ["python", "-m", "src.cli"]

