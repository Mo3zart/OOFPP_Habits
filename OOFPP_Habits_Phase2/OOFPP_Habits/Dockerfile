# ------------------------------
# Habit Tracker App - Dockerfile
# ------------------------------

# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV DB_PATH=/app/src/data/sample_habits.db
ENV TERM=xterm-256color

# Create and set working directory
WORKDIR /app

# Install SQLite3 ( for database & cli access)
RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 tree && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the project files into the container
COPY . .

# Ensure permissions are correct
RUN mkdir -p /app/src/data && chmod 777 /app/src/data

# Run tests automatically 
RUN pytest -v || true

# Run DB seeder before starting the app
RUN python -m src.modules.seed_db

# Define the default command for the CLI app
ENTRYPOINT ["python", "-m", "src.main"]

