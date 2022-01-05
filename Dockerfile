FROM python:3.7.12-slim

WORKDIR /app


# Base packages
RUN apt update && apt -y install curl \ 
    unzip \
    gnupg \
    libxml2-utils 

# Add signing key for repo
RUN curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Add repo for Google chrome
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install the latest Google chrome stable version and its corresponding chrome driver
RUN apt update &&  \
    apt -y install google-chrome-stable
RUN curl -s "https://chromedriver.storage.googleapis.com/" | \
        xmllint --xpath "//*[local-name()='Key']/text()" - | \
        grep -oP '.+(?=/chromedriver_linux64.zip)' | \
        grep `google-chrome-stable --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+(?=\.[0-9]+)'` | \
        sort -r | \
        head -n 1 | \
        xargs -iDRIVER_VERSION curl https://chromedriver.storage.googleapis.com/DRIVER_VERSION/chromedriver_linux64.zip -o /tmp/chromedriver_linux64.zip && \
        unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/

# debugging tools for selenium
RUN apt -y install xserver-xorg \ 
                    x11-apps \
                    fonts-ipafont-gothic
ENV DISPLAY=host.docker.internal:0

RUN pip install selenium \
                pyfields \
                pyaml \
                python-dotenv \
                click \
                pandas

COPY --chown=python . /app
RUN pip install .
CMD ["pyjiminy"]