# The number of nodes/computers connected to the LAN (variable).
N = 1
# Average packet arrival rate (packets/second) (variable). 
# Data packets arrive at the MAC layer following a Poisson 
# process at all nodes.
A = 1
# The speed of the LAN/channel/bus (fixed).
R = 1
# Packet length (fixed).
L = 1
# Distance between adjacent nodes on the bus/channel.
D = 1
# Propagation speed
S = 1

T_sim = 1000

# Exponential random number generator
def expn_random(rate):
    return (-(1/rate) * log(1 - random.uniform(0, 1)))

