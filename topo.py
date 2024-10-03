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
    hosts = {f'h{i}': f'10.0.0.{i}' for i in range(1, 17)}
    docker_hosts = {name: net.addDocker(name, ip=ip, dimage="mnhost") for name, ip in hosts.items()}

    info('*** Adding Switches (Core, Aggregation, Access)\n')
    
    # Core switches (two core switches)
    core_switches = {
        'core1': net.addSwitch('s1', protocols='OpenFlow14'),
        'core2': net.addSwitch('s2', protocols='OpenFlow14')
    }

    # Aggregation switches (four aggregation switches)
    aggregation_switches = {
        'aggr1': net.addSwitch('s3', protocols='OpenFlow14'),
        'aggr2': net.addSwitch('s4', protocols='OpenFlow14'),
        'aggr3': net.addSwitch('s5', protocols='OpenFlow14'),
        'aggr4': net.addSwitch('s6', protocols='OpenFlow14')
    }

    # Access switches (eight access switches)
    access_switches = {
        f'acc{i}': net.addSwitch(f's{i+6}', protocols='OpenFlow14') for i in range(1, 9)
    }

    info('*** Creating Links (Core -> Aggregation -> Access -> Hosts)\n')

    # Core to Aggregation: Redundant links (2 links from each core to each aggregation switch)
    for core in core_switches.values():
        for aggr in aggregation_switches.values():
            net.addLink(core, aggr)  # First link
            net.addLink(core, aggr)  # Redundant link

    # Aggregation to Access: Redundant links (2 links from each aggregation to each access switch)
    net.addLink(aggregation_switches['aggr1'], access_switches['acc1'])
    net.addLink(aggregation_switches['aggr1'], access_switches['acc1'])  # Redundant
    net.addLink(aggregation_switches['aggr1'], access_switches['acc2'])
    net.addLink(aggregation_switches['aggr1'], access_switches['acc2'])  # Redundant
    
    net.addLink(aggregation_switches['aggr2'], access_switches['acc3'])
    net.addLink(aggregation_switches['aggr2'], access_switches['acc3'])  # Redundant
    net.addLink(aggregation_switches['aggr2'], access_switches['acc4'])
    net.addLink(aggregation_switches['aggr2'], access_switches['acc4'])  # Redundant
    
    net.addLink(aggregation_switches['aggr3'], access_switches['acc5'])
    net.addLink(aggregation_switches['aggr3'], access_switches['acc5'])  # Redundant
    net.addLink(aggregation_switches['aggr3'], access_switches['acc6'])
    net.addLink(aggregation_switches['aggr3'], access_switches['acc6'])  # Redundant
    
    net.addLink(aggregation_switches['aggr4'], access_switches['acc7'])
    net.addLink(aggregation_switches['aggr4'], access_switches['acc7'])  # Redundant
    net.addLink(aggregation_switches['aggr4'], access_switches['acc8'])
    net.addLink(aggregation_switches['aggr4'], access_switches['acc8'])  # Redundant

    # Access to Hosts: Single links from access to hosts
    for i in range(1, 9):
        net.addLink(access_switches[f'acc{i}'], docker_hosts[f'h{2*i-1}'])
        net.addLink(access_switches[f'acc{i}'], docker_hosts[f'h{2*i}'])

    info('*** Starting Network\n')
    net.start()

    info('*** Connecting switches to controllers\n')
    for switch in core_switches.values():
        switch.start([controller1, controller2, controller3])
    for switch in aggregation_switches.values():
        switch.start([controller1, controller2, controller3])
    for switch in access_switches.values():
        switch.start([controller1, controller2, controller3])

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping Network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('debug')
    customSDNTopo()

