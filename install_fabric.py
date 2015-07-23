#!/usr/bin/python

import os
import sys
import fboss_ipaddr as ip

def syscmd(cmd):
    print cmd
    os.system(cmd)

if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print "Usage: %s <rowID> <fabricID> <wedgeCount>" % sys.argv[0]
        sys.exit()
    rowID = int(sys.argv[1])
    if (rowID == 0):
        print "Row ID must start from 1"
        sys.exit()
    fabricID = int(sys.argv[2])
    if (fabricID == 0):
        print "fabric ID must start from 1"
        sys.exit()
    wedgeCount = int(sys.argv[3])
    
    bridgeID = 1
    vlanList = []
    for i in range(wedgeCount):
        wedgeID = i + 1
        macAddr = ip.fabricMacAddr(fabricID, wedgeID)
        hostBridge = "br%s" % bridgeID 
        vlanID = (wedgeID + (fabricID * 48))
        vlanList.append(vlanID)
        vlanIntf = "vlan%s" % vlanID
        if ((i % 6) == 0):
            syscmd("ovs-vsctl --may-exist add-br %s" % hostBridge)
        syscmd("ovs-vsctl --may-exist add-port %s %s tag=%s" % (hostBridge, vlanIntf, vlanID))
        syscmd("ovs-vsctl set interface %s type=internal" % vlanIntf)
        syscmd("ifconfig %s %s netmask %s" % \
               (vlanIntf, ip.fabricIpAddr(fabricID, wedgeID), ip.fabricIpNetmask()))
        syscmd("route add -net %s netmask %s gw %s" % \
              (ip.wedgeIpSubnet(rowID, wedgeID), ip.wedgeIpNetmask(), \
               ip.wedgeUpIpAddr(fabricID, wedgeID)))

        if (((i % 6) == 5) or (i == (wedgeCount - 1))):
            vlanListStr = ""
            while (len(vlanList)):
                vlanID = vlanList.pop(0);
                if (len(vlanList)):
                    vlanListStr += '%s,' % vlanID
                else:
                    vlanListStr += '%s' % vlanID
            syscmd("ovs-vsctl --may-exist add-port %s gre%s vlan_mode=native-tagged" % \
                   (hostBridge, bridgeID))
            syscmd("ovs-vsctl set port gre%s trunks=%s" % (bridgeID, vlanListStr))
            syscmd("ovs-vsctl set interface gre%s type=gre options:remote_ip=192.168.2.%s" % (bridgeID, bridgeID))
            bridgeID += 1
    
    # enable ip forwarding
    syscmd("sysctl -w net.ipv4.ip_forward=1")
