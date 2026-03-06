FROM python:3.10-slim

# ---- system dependencies (IMPORTANT for pycairo) ----
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---- python deps ----
COPY ./requirements.txt /requirements.txt

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools wheel && \
    /py/bin/pip install -r /requirements.txt

# ---- app setup ----
COPY . /app
WORKDIR /app

# RUN /py/bin/python manage.py collectstatic --noinput


# ---- non-root user ----
RUN adduser --disabled-password --no-create-home django-user

ENV PATH="/py/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER django-user

# ---- gunicorn ----
CMD exec gunicorn gcc_backend.wsgi:application \
      --bind 0.0.0.0:${PORT:-8000} \
      --workers 3 \
      --threads 4 \
      --worker-class gthread \
      --timeout 120