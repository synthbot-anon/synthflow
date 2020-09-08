from synthbot/synthflow-cuda10.2:latest

# Make sure installation scripts don't ask for input
ENV DEBIAN_FRONTEND=noninteractive

# Install any extra packages for specialization
COPY /build-data/spec/ /tmp/spec/
RUN /tmp/spec/pre-install.sh
RUN apt-get update && \
  apt-get install -y $(cat /tmp/spec/packages.txt)
RUN pip3 install -r /tmp/spec/requirements.txt
RUN /tmp/spec/post-install.sh

# Set up the default execution environment
USER celestia
WORKDIR /home/celestia
