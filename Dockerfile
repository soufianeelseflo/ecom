FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && apt-get clean && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium
COPY . .
CMD ["python", "main.py"]