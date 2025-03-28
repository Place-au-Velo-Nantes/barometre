FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE 1    \
    PYTHONUNBUFFERED 1

RUN mkdir -p /var/log/pav/
RUN mkdir -p /usr/local/

# RUN apt-get install python3-virtualenv

# --------
FROM base AS dev

WORKDIR /app
RUN useradd -ms /bin/bash dev
RUN chown -R dev:dev /app

RUN chown dev:dev /var/log/pav/

USER dev
RUN mkdir /home/dev/.ssh/ && chmod  700 /home/dev/.ssh/

USER dev

COPY requirements.txt /app/
RUN python3 -m venv /home/dev/venv && . /home/dev/venv/bin/activate && pip install --upgrade pip && pip install -r /app/requirements.txt

# --------
FROM dev AS app

# Note that I'll mount a volume during dev so that I see updates.
USER dev
COPY . /app/
WORKDIR /app

# Expose the port Django will run on
EXPOSE 8200

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
