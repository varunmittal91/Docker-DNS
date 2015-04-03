from debian

MAINTAINER Varun Mittal
RUN apt-get update && apt-get install python-requests dnsmasq procps -y
RUN apt-get autoclean

ADD main.py /bin/main.py
ADD restartdns.sh /bin/restartdns.sh
ADD dnsmasq.conf /etc/dnsmasq.conf

EXPOSE 53/udp
EXPOSE 538/tcp

ENTRYPOINT ["/usr/bin/python", "/bin/main.py"]
