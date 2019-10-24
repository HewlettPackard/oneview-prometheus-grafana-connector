FROM python:3.6-alpine

# Set proxy
ARG http_proxy
ENV HTTP_PROXY=$http_proxy
ENV HTTPS_PROXY=$http_proxy

# Copy requirements.txt file to install dependencies
COPY requirements.txt /plugin/requirements.txt
COPY packages /plugin/packages
COPY internal /plugin/internal
COPY ov_client /plugin/ov_client
COPY main.py /plugin/main.py

WORKDIR /plugin

# Install Dependencies
RUN pip install --no-index --find-links=packages -r requirements.txt

# Run the plugin
CMD ["python","main.py","-i","/conf/config.json"]
