FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Creating workspace
ENV WORKSPACE=/usr/src/app
RUN mkdir -p $WORKSPACE
WORKDIR $WORKSPACE

# Project dependency
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY ./endpoint_1/ $WORKSPACE