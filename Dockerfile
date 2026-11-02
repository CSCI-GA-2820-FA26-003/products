FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies from the lock file
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --no-cache-dir pipenv \
    && pipenv sync --system \
    && python -m pip uninstall -y pipenv

# Copy the service and its entry point
COPY service/ ./service/
COPY wsgi.py ./

ENV PORT=8080
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--log-level=info", "wsgi:app"]