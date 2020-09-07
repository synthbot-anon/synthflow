from nvidia/cuda:10.2-devel

# Default value for what additional setup to perform
ARG SPECIALIZATION="synthbot"

# Make sure installation scripts don't ask for input
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y --no-install-recommends wget

# Copy in baseline scripts for setting up the container
COPY ./build-data/pre-install.sh /tmp/pre-install.sh
COPY ./build-data/packages.txt /tmp/packages.txt
COPY ./build-data/requirements.txt /tmp/requirements.txt
COPY ./build-data/post-install.sh /tmp/post-install.sh
COPY ./build-data/pre-run.sh /tmp/pre-run.sh

# Install all baseline packages
RUN /tmp/pre-install.sh
RUN apt-get install -y $(cat /tmp/packages.txt)
RUN pip3 install -U pip
RUN pip3 install -r /tmp/requirements.txt
RUN /tmp/post-install.sh

# Install Montreal Forced Aligner
COPY ./build-data/mfa /opt/mfa

# Install any extra packages for specialization
COPY /build-data/spec/${SPECIALIZATION}/ /tmp/spec/
RUN /tmp/spec/pre-install.sh
RUN apt-get install -y $(cat /tmp/spec/packages.txt)
RUN pip3 install -r /tmp/spec/requirements.txt
RUN /tmp/spec/post-install.sh

# Set up user celestia
RUN adduser --disabled-password --gecos "" celestia
USER celestia
COPY --chown=celestia ./build-data/bashrc /home/celestia/.bashrc
COPY --chown=celestia ./build-data/inputrc /home/celestia/.inputrc

# Set up the default execution environment
USER root
WORKDIR /home/celestia
