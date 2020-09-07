from nvidia/cuda:latest

# Default value for what additional setup to perform
ARG SPECIALIZATION="synthbot"

# Make sure installation scripts don't ask for input
ENV DEBIAN_FRONTEND=noninteractive

# Copy in baseline scripts for setting up the container
COPY ./build-data/preinstall.sh /tmp/preinstall.sh
COPY ./build-data/packages.txt /tmp/packages.txt
COPY ./build-data/requirements.txt /tmp/requirements.txt
COPY ./build-data/post-setup.sh /tmp/post-setup.sh

# Install all baseline packages
RUN /tmp/preinstall.sh
RUN apt-get update && \
  apt-get install -y --no-install-recommends $(cat /tmp/packages.txt)
RUN pip3 install -r /tmp/requirements.txt

# Install Montreal Forced Aligner
COPY ./build-data/mfa /opt/mfa

# Install any extra packages for specialization
COPY /build-data/spec/${SPECIALIZATION}/ /tmp/spec/
RUN /tmp/spec/preinstall.sh
RUN apt-get install -y --no-install-recommends $(cat /tmp/spec/packages.txt)
RUN pip3 install -r /tmp/spec/requirements.txt

# Set up user celestia
RUN adduser --disabled-password --gecos "" celestia
USER celestia
COPY --chown=celestia ./build-data/bashrc /home/celestia/.bashrc
COPY --chown=celestia ./build-data/inputrc /home/celestia/.inputrc

# Set up the default execution environment
USER root
WORKDIR /home/celestia
