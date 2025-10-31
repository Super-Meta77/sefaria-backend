# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install venv module if not present and create a virtual environment
RUN apt-get update && apt-get install -y python3-venv && \
    python3 -m venv /opt/venv

# Ensure virtualenv executables are in the path
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip inside the virtual environment
RUN /opt/venv/bin/pip install --upgrade pip

# Copy the requirements file and install dependencies in the virtual environment
COPY ./requirements.txt /app/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy your application code
COPY ./ /app/

# Expose port 80
EXPOSE 80

# Command to run your FastAPI application with Uvicorn using the virtual environment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]