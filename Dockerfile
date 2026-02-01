# Use official Python base image
FROM python:3.11-slim

# Executar como usuário não-root (segurança)
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/false --create-home appuser

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=appuser:appgroup . .

# Garantir permissões
RUN chown -R appuser:appgroup /app

USER appuser

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]