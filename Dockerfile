# Set up Python Environment
FROM python:3.10

# Install build dependencies
RUN apt update && \
    apt install -y default-jdk && \
    apt install -y gcc && \
    apt install -y zip && \
    apt install -y nano

# We install the Java JDK for opening microscope images, gcc for compilation of the python-javabridge package, zip for packaging the output, and nano for editing files in the container.

# Set JAVA_HOME and update PATH
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="$JAVA_HOME/bin:$PATH"

# Then install your package
WORKDIR /app
RUN mkdir /app/FlickerPrint
COPY . /app/FlickerPrint

RUN cd /app/FlickerPrint/src && \
    python3 -m pip install . && \
    cd /app

CMD ["bash"]