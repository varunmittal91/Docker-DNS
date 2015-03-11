### Docker DNS update service ###

## SELINUX
 If running with selinux(recommended). 
 Please install the policy for allowing socket communication in the docker image.

> Run this command on host machine.

> selinux_module: https://github.com/varunmittal91/Docker-DNS/raw/master/selinux_module/docker_dns.pp

> semodule -i docker_dns.pp

> docker run -d -p <host_ip>:53:53/udp -v /var/run/docker.sock:/var/run/docker.sock --dns local_dns1,local_dns2,local_dns2

> On host machine 53/udp has to be enabled

