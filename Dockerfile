FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set environment variables at runtime, not build time
ENV PYTHONUNBUFFERED=1

# Create a startup script that loads environment variables
RUN echo '#!/bin/bash\n\
if [ -f service.json ]; then\n\
  echo "Loading environment variables from service.json"\n\
  if [ -x "$(command -v jq)" ]; then\n\
    export OPENROUTER_API_KEY=$(jq -r ".environments.production.env.OPENROUTER_API_KEY" service.json 2>/dev/null || echo "")\n\
    export SECRET_KEY=$(jq -r ".environments.production.env.SECRET_KEY" service.json 2>/dev/null || echo "")\n\
    export APP_URL=$(jq -r ".environments.production.env.APP_URL" service.json 2>/dev/null || echo "")\n\
  else\n\
    echo "jq not installed, relying on Python to load variables"\n\
  fi\n\
fi\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Install jq utility to parse JSON in bash
RUN apt-get update && apt-get install -y jq && apt-get clean

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

EXPOSE 8080

# Use the entrypoint script to load environment variables
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"] 
