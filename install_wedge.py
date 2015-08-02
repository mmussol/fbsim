#!/usr/bin/python

import os
import sys
import fboss_ipaddr as ip

def syscmd(cmd):
    print cmd
    os.system(cmd)

def installWedge(rowID, startWedgeID, wedgeCount, fabricCount):
    # download lxc base container
    if not os.path.exists("/var/lib/lxc/lxc-base"):
        print "Downloading base lxc container"
        syscmd("wget http://duewfii2efk8c.cloudfront.net/lxc-base.tgz")
        syscmd("tar --numeric-owner -zxf lxc-base.tgz -C /")
        syscmd("rm -f lxc-base.tgz")
    
    vlanList = []
    for i in range(fabricCount):
        vlanList.append([])
    
    syscmd("rm -f start.sh")
    syscmd("rm -f stop.sh")
    
    # clone / configure wedge container(s)
    for i in range(wedgeCount):
        wedgeID = startWedgeID + i
        lxcName = "lxc-wedge%s" % wedgeID 
        dir = "/var/lib/lxc/%s" % lxcName
        if not os.path.exists(dir):
            syscmd("lxc-clone lxc-base %s" % lxcName)
        syscmd("echo 'lxc-start -d -n %s' >> start.sh" % lxcName)
        syscmd("echo 'lxc-stop -n %s' >> stop.sh" % lxcName)

        # Port forwarding for fboss agent port
        hostIpAddr = "10.0.3.10%s" % (i + 1)
        fbossPort = 5900 + (i + 1);
        syscmd("echo 'iptables -t nat -A PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s' >> start.sh" % \
                (fbossPort, hostIpAddr, fbossPort))
        syscmd("echo 'iptables -A FORWARD -p tcp -d %s --dport %s -j ACCEPT' >> start.sh" % \
               (hostIpAddr, fbossPort))
        syscmd("echo 'iptables -t nat -D PREROUTING -p tcp --dport %s -j DNAT --to-destination %s:%s' >> stop.sh" % \
                (fbossPort, hostIpAddr, fbossPort))
        syscmd("echo 'iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT' >> stop.sh" % \
               (hostIpAddr, fbossPort))
    
        # Copy fboss init scripts
        syscmd("cp fboss*.py %s/rootfs/root/" % dir)
        fbossScript = "%s/rootfs/etc/init.d/fboss" % dir
        syscmd("cp init.d.fboss.wedge %s.temp1" % fbossScript)
        syscmd("sed s/DUMMY_ROW_ID/%s/g %s.temp1 > %s.temp2" % \
              (rowID, fbossScript, fbossScript))
        syscmd("sed s/DUMMY_WEDGE_ID/%s/g %s.temp2 > %s.temp3" % \
              (wedgeID, fbossScript, fbossScript))
        syscmd("sed s/DUMMY_FABRIC_COUNT/%s/g %s.temp3 > %s.temp4" % \
              (fabricCount, fbossScript, fbossScript))
        syscmd("sed s@DUMMY_FBOSS_JSON@%s@g %s.temp4 > %s.temp5" % \
              ("/root/fbbin/sample1.json", fbossScript, fbossScript))
        syscmd("sed s/DUMMY_FBOSS_PORT/%s/g %s.temp5 > %s" % \
              (fbossPort, fbossScript, fbossScript))
        syscmd("rm -f %s.temp*" % fbossScript)
        syscmd("chmod +x %s" % fbossScript)
    
        # Assign static IP address for "management" ethernet
        syscmd("echo 'lxc.network.type = veth' >> %s/config" % dir)
        syscmd("echo 'lxc.network.flags = up' >> %s/config" % dir)
        syscmd("echo 'lxc.network.link = lxcbr0' >> %s/config" % dir)
        syscmd("echo 'lxc.network.hwaddr = 00:16:0a:00:03:0%s' >> %s/config" % ((i + 1), dir))
        syscmd("echo 'lxc.network.ipv4 = %s/24' >> %s/config" % (hostIpAddr, dir))

        # Fill in lxc network config. One interface per fabric uplink
        for j in range(fabricCount):
            fabricID = j + 1
            syscmd("echo 'lxc.network.type = veth' >> %s/config" % dir)
            syscmd("echo 'lxc.network.flags = up' >> %s/config" % dir)
            syscmd("echo 'lxc.network.veth.pair = w%seth%s' >> %s/config" % (wedgeID, fabricID, dir))
            macAddr = ip.wedgeUpMacAddr(fabricID, wedgeID)
            syscmd("echo 'lxc.network.hwaddr = %s' >> %s/config" % (macAddr, dir))
            ovsup = "%s/ovsup.fab%s" % (dir, fabricID)
            syscmd("echo 'lxc.network.script.up = %s' >> %s/config" % (ovsup, dir))
    
            # Fill in the ovsup script
            syscmd("echo '#!/bin/bash' >> %s" % ovsup)
            hostBridge = "br%s" % fabricID
            syscmd("echo 'HOST_BRIDGE=\"%s\"' >> %s" % (hostBridge, ovsup))
            syscmd("echo 'ovs-vsctl del-br %s' >> stop.sh" % hostBridge)
            vlanID = (wedgeID + (fabricID * 48))
            vlanList[j].append(vlanID)
            syscmd("echo 'VLAN=\"vlan%s\"' >> %s" % (vlanID, ovsup))
            syscmd("echo 'VLAN_TAG=\"%s\"' >> %s" % (vlanID, ovsup))
            syscmd("echo 'ovs-vsctl --may-exist add-br $HOST_BRIDGE' >> %s" % ovsup)
            syscmd("echo 'ovs-vsctl --if-exists del-port $HOST_BRIDGE $5' >> %s" % ovsup)
            syscmd("echo 'ovs-vsctl --may-exist add-port $HOST_BRIDGE $5 tag=$VLAN_TAG' >> %s" % ovsup)
            syscmd("chmod +x %s" % ovsup)
    

    # The first wedge containter in the system will set up GRE tunnels to fabric(s)
    wedgeID = startWedgeID 
    lxcName = "lxc-wedge%s" % wedgeID
    dir = "/var/lib/lxc/%s" % lxcName
    

    # Fill in lxc network config. One interface per fabric uplink
    for j in range(fabricCount):
        fabricID = j + 1 
        ovsup = "%s/ovsup.fab%s" % (dir, fabricID)
        vlanListStr = ""
        while (len(vlanList[j])):
            vlanID = vlanList[j].pop(0);
            if (len(vlanList[j])):
                vlanListStr += '%s,' % vlanID
            else:
                vlanListStr += '%s' % vlanID
        syscmd("echo 'ovs-vsctl --may-exist add-port $HOST_BRIDGE gre%s vlan_mode=native-tagged' >> %s" % (fabricID, ovsup))
        syscmd("echo 'ovs-vsctl set port gre%s trunks=%s' >> %s" % (fabricID, vlanListStr, ovsup))
        syscmd("echo 'ovs-vsctl set interface gre%s type=gre options:remote_ip=192.168.3.%s' >> %s" % (fabricID, fabricID, ovsup))
    
    syscmd("chmod +x start.sh")
    syscmd("chmod +x stop.sh")
    syscmd("lxc-destroy -n lxc-base")

if __name__ == '__main__':
    if (len(sys.argv) < 5):
        print "Usage: %s <rowID> <starting wedgeID> <wedgeCount> <fabricCount>" % sys.argv[0]
        sys.exit()
    rowID = int(sys.argv[1])
    if (rowID == 0):
        print "Row ID must start from 1"
        sys.exit()
    if not os.path.exists("init.d.fboss.wedge"):
        print "init.d.fboss.wedge file not found. Running script from wrong place?"
        sys.exit()
    startWedgeID = int(sys.argv[2])
    if (startWedgeID == 0):
        print "wedge ID must start from 1"
        sys.exit()
    wedgeCount = int(sys.argv[3])
    fabricCount = int(sys.argv[4])
    installWedge(rowID, startWedgeID, wedgeCount, fabricCount)
