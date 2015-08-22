# README #

Facebook datacenter fabric simulator running in Amazon AWS. TOR switches and hosts are simulated with Mininet; LXC containers for route table isolation. The containers are running FB opensource "sim_agent" for adding routes, "fboss_route.py" sample app sends routes via FB Thrift.

See presentation for more details:
https://docs.google.com/presentation/d/1EgE5UsyulEeM7Cg10I3Wb6Ggq3yhUuNk4Gven3_Gqwc/edit?usp=sharing