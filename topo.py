#!/usr/bin/python3

from mininet.net import Containernet
from mininet.node import RemoteController, OVSSwitch
from mininet.log import setLogLevel, info
from mininet.cli import CLI

def customSDNTopo():
    net = Containernet(controller=RemoteController, switch=OVSSwitch)

    info('*** Adding Remote Controllers (OpenFlow 1.0)\n')
    # Remote controllers on different ports with OpenFlow 1.0
    controller1 = net.addController('c1', ip='127.0.0.1', port=6653)
    controller2 = net.addController('c2', ip='127.0.0.1', port=6654)
    controller3 = net.addController('c3', ip='127.0.0.1', port=6655)

    info('*** Adding Docker Hosts (using mnhost image)\n')
    hosts = {
        'user': '10.0.0.1', 'admin': '10.0.0.2',
        'h1': '10.0.0.3', 'h2': '10.0.0.4', 'h3': '10.0.0.5', 'h4': '10.0.0.6',
        'h5': '10.0.0.7', 'h6': '10.0.0.8', 'h7': '10.0.0.9', 'h8': '10.0.0.10'
    }
    
    docker_hosts = {name: net.addDocker(name, ip=ip, dimage="mnhost") for name, ip in hosts.items()}

    info('*** Adding Switches\n')
    switches = {f's{i}': net.addSwitch(f's{i}', protocols='OpenFlow14') for i in range(1, 6)}

    info('*** Creating Links\n')
    net.addLink(docker_hosts['user'], switches['s5'])
    net.addLink(docker_hosts['admin'], switches['s5'])

    for i, switch in enumerate(switches.values(), start=1):
        if i < 5:
            net.addLink(switch, docker_hosts[f'h{i*2-1}'])
            net.addLink(switch, docker_hosts[f'h{i*2}'])
            net.addLink(switch, switches['s5'])

    info('*** Starting Network\n')
    net.start()

    info('*** Connecting switches to controllers\n')
    for switch in switches.values():
        switch.start([controller1, controller2, controller3])

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping Network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('debug')
    customSDNTopo()

