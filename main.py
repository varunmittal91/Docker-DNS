import requests_unixsocket
import json
from time import sleep
import os
from subprocess import call
import getopt
from sys import argv, exit
import requests

container_list = {}

def add_dns(name, hostname, ip, is_slave=None):
    if is_slave:
        r = requests.put("http://%s/%s/%s/%s/" % (is_slave, name, hostname, ip))
        if r.status_code != 200:
            exit(0)
    else:
        file = open("/etc/dnsmasq.d/0%s" % hostname, "w+")
        file.write("host-record=%s,%s" % (hostname,ip))
        file.close()
def remove_dns(hostname, is_slave=None):
    if is_slave:
        r = requests.delete("http://%s/%s/" % (is_slave, hostname))
        if r.status_code != 200:
            exit(0)
    else:
        return call(["rm", "/etc/dnsmasq.d/0%s" % hostname])

file_path = "http+unix://%2Fvar%2Frun%2Fdocker.sock"
def get_response(api_path):
    session = requests_unixsocket.Session()
    r = session.get("%s/%s" % (file_path, api_path))
    if r.status_code == 200:
        return json.loads(r.content)

def update_dns(is_slave=None):
    containers = get_response('containers/json?all=1')
    dnsmasq_required_restart = False

    listed_ids = []

    for container in containers:
        listed_ids.append(container['Id'])

        is_up = False
        if container['Status'].startswith('Up'):
            is_up = True
        try:
            status = container_list[container['Id']]
            if is_up:
                container_status = get_response('containers/%s/json' % container['Id'])
                if container_status['NetworkSettings']['IPAddress'] != status['ip']:
                    add_dns(name=container_status['Name'][1:], hostname=container_status['Config']['Hostname'],
                                ip=container_status['NetworkSettings']['IPAddress'], is_slave=is_slave)
                    status['ip'] = container_status['NetworkSettings']['IPAddress']
                    dnsmasq_required_restart = True
        except KeyError:
            if is_up:
                container_status = get_response('containers/%s/json' % container['Id'])
                add_dns(name=container_status['Name'][1:], hostname=container_status['Config']['Hostname'], 
                            ip=container_status['NetworkSettings']['IPAddress'], is_slave=is_slave)
                dnsmasq_required_restart = True
                container_list[container['Id']] = {'hostname': container_status['Config']['Hostname'], 
                                                       'ip': container_status['NetworkSettings']['IPAddress']}

    stopped = set(container_list.keys()) - set(listed_ids)
    if len(stopped) > 0:
        dnsmasq_required_restart = True
        for id in stopped: 
            remove_dns(container_list[id]['hostname'], is_slave=is_slave)
            del container_list[id]

    if not is_slave and dnsmasq_required_restart:
        call(['/bin/restartdns.sh'])

optlist,args = getopt.getopt(argv[1:], '-d:-m:', ['dns=', 'master='])
names = ["127.0.0.1"]
is_slave = False
for opt,value in optlist:
    if opt in ['d', '--dns']:
        names.extend(value.split(','))
    elif opt in ['m', '--master']:
        is_slave = value
if not is_slave:
    resolve_file = open("/etc/resolv.dnsmasq.conf", "w+")
    names.append('8.8.8.8')
    [resolve_file.write("nameserver %s\n" % name) for name in names]
    resolve_file.close()

    import SimpleHTTPServer
    import SocketServer

    PORT = 538
    server_address = ('0.0.0.0', PORT)
    class UpdateDNS(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def _set_headers(self, status_code):
            self.send_response(status_code)
            self.end_headers()
        def do_GET(self): pass
        def do_DELETE(self):
            hostname = self.path[1:].split('/')[0]
            if len(hostname) > 0:
                if remove_dns(hostname) == 0:
                    call(['/bin/restartdns.sh'])
                self._set_headers(200)
            else:
                self._set_headers(500)
            self.wfile.write("")
        def do_PUT(self):
            try:
                name,hostname,ip = self.path[1:].split('/')[0:3]
                add_dns(name,hostname,ip)
                call(['/bin/restartdns.sh'])
                self._set_headers(200)
            except ValueError:
                self._set_headers(500)
            self.wfile.write("")
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(server_address, UpdateDNS)
    httpd.serve_forever()
else:
    while 1:
        update_dns(is_slave)
        sleep(10)
