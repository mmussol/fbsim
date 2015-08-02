#!/usr/bin/python

import os

def wedgeTeardown():
    # kill fboss sim_agent
    cmd = "ps axuw | grep 'sim_agent' | grep fbbin | awk '{print $2}' | xargs kill"
    print cmd ; os.system(cmd)

    # kill setup script which is running mininet CLI
    cmd = "ps aux | grep 'fboss_wedge_setup' | grep python | awk '{print $2}' | xargs kill"
    print cmd ; os.system(cmd)

    # kill OVS controller
    cmd = "killall ovs-controller"
    print cmd ; os.system(cmd)

if __name__ == '__main__':
    wedgeTeardown()


