#!/usr/bin/python

import socket, struct

def hostIpAddr(rowID, wedgeID, hostID):
    # HOST IP ADDRESS = 10.x.y.z
    #  x = rowID
    #  y = wedgeID
    #  z = hostID
    addr = 0x0a000000 + (rowID << 16) + (wedgeID << 8) + hostID
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def wedgeIpSubnet(rowID, wedgeID):
    # WEDGE downlink (towards hosts)
    # WEDGE IP ADDRESS = 10.x.y.0/24
    #  x = rowID
    #  y = wedgeID
    addr = 0x0a000000 + (rowID << 16) + (wedgeID << 8)
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def wedgeIpNetmask():
    # WEDGE downlink (towards hosts), /24
    return "255.255.255.0"

def wedgeIpAddr(rowID, wedgeID):
    # WEDGE downlink (towards hosts)
    # WEDGE IP ADDRESS = 10.x.y.128
    #  x = rowID
    #  y = wedgeID
    addr = 0x0a000000 + (rowID << 16) + (wedgeID << 8) + 128
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def wedgeUpIpAddr(fabricID, wedgeID):
    # WEDGE uplink (towards fabric)
    # WEDGE IP ADDRESS = 10.x.y.1
    #  x = fabricID + 64
    #  y = wedgeID
    addr = 0x0a000000 + ((fabricID + 64) << 16) + (wedgeID << 8) + 1
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def wedgeUpMacAddr(fabricID, wedgeID):
    # WEDGE uplink (towards fabric)
    # WEDGE MAC ADDRESS = 02:00:0a.x.y.01
    #  x = fabricID + 64
    #  y = wedgeID
    addr = "02:00:0a:%s:%s:01" % ('{:02x}'.format(fabricID + 64), '{:02x}'.format(wedgeID))
    return addr

def rowIpSubnet(rowID):
    # subnet for all hosts in row
    # 10.x.0.0 / 16
    addr = 0x0a000000 + (rowID << 16)
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def rowIpNetmask():
    return "255.255.0.0"

def fabricIpSubnet(fabricID, wedgeID):
    # FABRIC downlink (towards wedge)
    # SUBNET IP ADDRESS = 10.x.y.0/24
    #  x = fabricID + 64
    #  y = wedgeID
    addr = 0x0a000000 + ((fabricID + 64) << 16) + (wedgeID << 8)
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def fabricIpNetmask():
    # FABRIC downlink (towards wedge) /24 
    return "255.255.255.0"

def fabricIpAddr(fabricID, wedgeID):
    # FABRIC downlink (towards wedge)
    # FABRIC IP ADDRESS = 10.x.y.2
    #  x = fabricID + 64
    #  y = wedgeID  
    addr = 0x0a000000 + ((fabricID + 64) << 16) + (wedgeID << 8) + 2
    addrStr = socket.inet_ntoa(struct.pack('!L', addr))
    return addrStr

def fabricMacAddr(fabricID, wedgeID):
    # FABRIC downlink (towards wedge)
    # FABRIC MAC ADDRESS = 02:00:0a.x.y.02
    #  x = fabricID + 64
    #  y = wedgeID
    addr = "02:00:0a:%s:%s:02" % ('{:02x}'.format(fabricID + 64), '{:02x}'.format(wedgeID))
    return addr



