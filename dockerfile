# Use the official lightweight Python image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the dependencies file to the working directory.
COPY requirements.txt .

# Install any dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local directory to the working directory.
COPY . .

# Command to run on container start.
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
