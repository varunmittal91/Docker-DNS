## Docker DNS update service ##

# SELINUX
If running with selinux(recommended). 
Please install the policy for allowing socket communication in the docker image.

Run this command on host machine.
semodule -i docker_dns.pp
