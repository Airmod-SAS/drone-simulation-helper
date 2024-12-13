FROM cyberbotics/webots:latest

# Install numpy
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install numpy

# Set the entrypoint to bash
ENTRYPOINT ["/bin/bash"]