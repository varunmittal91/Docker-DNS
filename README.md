### Docker DNS update service ###

## SELINUX
 If running with selinux(recommended). 
 Please install the policy for allowing socket communication in the docker image.
> This creates a rule for allowing access to docker.sock from container.
> Run this command on host machine.
> selinux_module: https://github.com/varunmittal91/Docker-DNS/raw/master/selinux_module/docker_dns.pp
> semodule -i docker_dns.pp

## Running dns service
> DNS master, running dnsmasq
>
> docker run -d -p <HOST_IP>:53:53/udp -p <HOST_IP>:538:538/tcp --name dns_master varunmittal91/docker-dns
> 
> DNS Slave
>
> docker run -d -v /var/run/docker.sock:/var/run/docker.sock --name dns_slave varunmittal91/docker-dns --master <MASTER HOST_IP>:538 --docker_api <LOCAL DOCKER API>
> On host machine 53/udp has to be enabled


