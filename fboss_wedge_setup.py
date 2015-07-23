#!/usr/bin/python

import sys
import os
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
import fboss_ipaddr as ip

def syscmd(cmd):
    print cmd
    os.system(cmd)

def wedgeSetup(rowID, wedgeID, fabricCount):
    hostCount = 32 # TODO hard code for now

    # Use 'wedgeID %6' in the name!! Otherwise name is too long? and mininet can't start
    wedgeStr = "br.wedge%s" % (wedgeID % 6)

    # create mininet topology
    net = Mininet(controller = OVSController)
    controller = net.addController()
    print "adding switch %s" % wedgeStr
    wedge = net.addSwitch(wedgeStr)
    hosts = []
    for i in range(hostCount):
        hostID = i + 1
        hostStr = "h%s" % hostID 
        print "adding host %s" % hostStr
        hosts.append(net.addHost(hostStr))
        net.addLink(hosts[i], wedge)

    print "starting mininet network"
    net.start()

    # configure IP address for wedge switch
    syscmd("ifconfig %s %s netmask %s" % \
          (wedgeStr, ip.wedgeIpAddr(rowID, wedgeID), ip.wedgeIpNetmask()))

    # configure IP address for fabric uplink port(s)
    # start with "eth1"
    for i in range(fabricCount):
        fabricID = i + 1
        syscmd("ifconfig eth%s %s netmask %s" % \
              (fabricID, ip.wedgeUpIpAddr(fabricID, wedgeID), ip.fabricIpNetmask()))

    # enable IP forwarding
    syscmd("sysctl -w net.ipv4.ip_forward=1")

    # add route to wedge downlink subnet (towards hosts)
    syscmd("route add -net %s netmask %s gw %s" % \
          (ip.wedgeIpSubnet(rowID, wedgeID), ip.wedgeIpNetmask(), ip.wedgeIpAddr(rowID, wedgeID)))

    # add less-specific route to other racks via fabric link(s)
    for i in range(fabricCount):
        fabricID = i + 1
        syscmd("route add -net %s netmask %s gw %s" % \
              (ip.rowIpSubnet(rowID), ip.rowIpNetmask(), ip.fabricIpAddr(fabricID, wedgeID)))

    # configure host IP addresses
    for i in range(hostCount):
        hostID = i + 1
        hostStr = "h%s" % hostID 
        print "setting host %s ip addr = %s" % (hostStr, ip.hostIpAddr(rowID, wedgeID, hostID))
        hosts[i].setIP("%s/24" % ip.hostIpAddr(rowID, wedgeID, hostID))
        hosts[i].cmd("route add default gw %s" % ip.wedgeIpAddr(rowID, wedgeID))

    # start mininet command line interface
    CLI(net)

if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print "Usage: %s <rowID> <wedgeID> <fabricCount>" % sys.argv[0]
        sys.exit()
    rowID = int(sys.argv[1])
    if (rowID == 0):
        print "rowID must be > 0"
        sys.exit()
    wedgeID = int(sys.argv[2])
    fabricCount = int(sys.argv[3])
    wedgeSetup(rowID, wedgeID, fabricCount)

