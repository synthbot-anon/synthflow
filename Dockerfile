from python:latest

# Default value for what additional setup to perform
ARG SPECIALIZATION="synthbot"

# Make sure installation scripts don't ask for input
ENV DEBIAN_FRONTEND=noninteractive

# Copy in baseline scripts for setting up the container
COPY ./build-data/preinstall.sh /tmp/preinstall.sh
COPY ./build-data/packages.txt /tmp/packages.txt
COPY ./build-data/requirements.txt /tmp/requirements.txt

# Install all baseline packages
RUN sh -c '/tmp/preinstall.sh'
RUN apt-get update && \
  apt-get install -y --no-install-recommends $(cat /tmp/packages.txt)
RUN pip3 install -r /tmp/requirements.txt

# Install Montreal Forced Aligner
COPY ./build-data/mfa /opt/mfa

# Post-installation setup scripts
RUN adduser --disabled-password --gecos "" celestia
COPY ./build-data/post-setup.sh /tmp/post-setup.sh
RUN /tmp/post-setup.sh

# Install any extra packages for specialization
COPY ./build-data/specialization/${SPECIALIZATION}/packages.txt /tmp/specialization/packages.txt
COPY ./build-data/specialization/${SPECIALIZATION}/requirements.txt /tmp/specialization/requirements.txt
RUN apt-get update && \
  apt-get install -y --no-install-recommends $(cat /tmp/specialization/packages.txt)
RUN pip3 install -r /tmp/specialization/requirements.txt

# Set up the user environment for celestia
USER celestia
ENV AIRFLOW_HOME=/data/airflow
COPY --chown=celestia ./build-data/bashrc /home/celestia/.bashrc
COPY --chown=celestia ./build-data/inputrc /home/celestia/.inputrc

# Set up the default execution environment
USER root
WORKDIR /home/celestia
