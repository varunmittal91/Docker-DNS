from debian

MAINTAINER Varun Mittal
RUN apt-get update && apt-get install python-pip dnsmasq procps -y
RUN pip install requests_unixsocket

ADD main.py /bin/main.py
ADD restartdns.sh /bin/restartdns.sh
ADD dnsmasq.conf /etc/dnsmasq.conf

VOLUME ["/var/run/docker.sock"]
EXPOSE 53/udp
EXPOSE 538/tcp

ENTRYPOINT ["/usr/bin/python", "/bin/main.py"]
