# Dockerfile
# Stage 1: build frontend
FROM node:20 AS frontend-build
WORKDIR /app/frontend
# Copy config files and index.html
COPY frontend/package*.json frontend/tsconfig*.json frontend/vite.config.ts frontend/postcss.config.js frontend/tailwind.config.js frontend/index.html ./
# Copy source and public assets
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm ci && npm run build

# Stage 2: Python runtime
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
# Install system deps that might be needed by some packages (adjust as necessary)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend into a folder the backend can serve (adjust backend to serve from ./frontend_dist)
COPY --from=frontend-build /app/frontend/dist ./frontend_dist

# Expose port and run uvicorn (change module path if needed)
EXPOSE 8080
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
