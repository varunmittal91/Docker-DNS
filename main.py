import requests_unixsocket
import json
from time import sleep
import os
from subprocess import call
import getopt
from sys import argv

container_list = {}

def add_dns(name, hostname, ip):
    file = open("/etc/dnsmasq.d/0%s" % hostname, "w+")
    file.write("host-record=%s,%s" % (hostname,ip))
    file.close()
def remove_dns(hostname):
    call(["rm", "/etc/dnsmasq.d/0%s" % hostname])

file_path = "http+unix://%2Fvar%2Frun%2Fdocker.sock"
def get_response(api_path):
    session = requests_unixsocket.Session()
    r = session.get("%s/%s" % (file_path, api_path))
    if r.status_code == 200:
        return json.loads(r.content)

def update_dns():
    containers = get_response('containers/json?all=1')
    dnsmasq_required_restart = False
    for container in containers:
        is_up = False
        if container['Status'].startswith('Up'):
            is_up = True
        try:
            status = container_list[container['Id']]
            if not is_up:
                dnsmasq_required_restart = True
                remove_dns(status)
                del container_list[container['Id']]
                dnsmasq_required_restart = True
        except KeyError:
            if is_up:
                container_status = get_response('containers/%s/json' % container['Id'])
                add_dns(name=container_status['Name'][1:], hostname=container_status['Config']['Hostname'], 
                            ip=container_status['NetworkSettings']['IPAddress'])
                dnsmasq_required_restart = True
                container_list[container['Id']] = container_status['Config']['Hostname']
    if dnsmasq_required_restart:
        call(['/bin/restartdns.sh'])

optlist,args = getopt.getopt(argv[1:], '-d:', ['dns='])
names = ["127.0.0.1"]
resolve_file = open("/etc/resolv.dnsmasq.conf", "w+")
for opt,value in optlist:
    names.extend(value.split(','))
names.append('8.8.8.8')
[resolve_file.write("nameserver %s\n" % name) for name in names]
resolve_file.close()

while 1:
    update_dns()
    sleep(10)
