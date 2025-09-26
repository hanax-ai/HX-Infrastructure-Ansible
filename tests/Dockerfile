
# Dockerfile for testing Ansible automation platform
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    openssh-server \
    sudo \
    curl \
    wget \
    git \
    vim \
    systemctl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install \
    ansible \
    ansible-lint \
    yamllint \
    molecule \
    pytest \
    pytest-testinfra

# Create ansible user
RUN useradd -m -s /bin/bash ansible && \
    echo 'ansible:ansible' | chpasswd && \
    usermod -aG sudo ansible && \
    echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Configure SSH
RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create working directory
WORKDIR /ansible

# Copy test files
COPY . /ansible/

# Set ownership
RUN chown -R ansible:ansible /ansible

# Switch to ansible user
USER ansible

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]

