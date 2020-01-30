FROM debian:latest
RUN apt update \
    && apt install -y less python3 rename \
    && apt-get clean; rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*
COPY move_wipedrive_xml.py /usr/local/bin/move_wipedrive
COPY flattendir.sh /usr/local/bin/flattendirs
