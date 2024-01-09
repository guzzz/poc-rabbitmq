FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Creating workspace
ENV WORKSPACE=/usr/src/app
RUN mkdir -p $WORKSPACE
WORKDIR $WORKSPACE

# Project dependency
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY consumer/ $WORKSPACE