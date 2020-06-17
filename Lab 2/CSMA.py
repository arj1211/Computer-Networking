from math import log
import random

# The number of nodes/computers connected to the LAN (variable).
N = 10
# Average packet arrival rate (packets/second) (variable). 
# Data packets arrive at the MAC layer following a Poisson 
# process at all nodes.
A = 2
# The speed of the LAN/channel/bus (fixed).
R = 20
# Packet length (fixed).
L = 5
# Distance between adjacent nodes on the bus/channel.
D = 100
# Propagation speed
S = 25

T_sim = 1000

# Exponential random number generator
def expn_random(rate):
    return (-(1/rate) * log(1 - random.uniform(0, 1)))

# Create arrival events
def gen_arrivals(rate):
    arrival_events = []
    t = expn_random(rate) # time of first pkt arrival
    while t < T_sim:
        arrival_events.append(t)
        t += expn_random(rate)
    return arrival_events


# Do for multiple T_sims
while T_sim <= 3000:
    # Set up queues for each of N nodes
    Q = [gen_arrivals(A) for i in range(N)]
    # find first sending node
    mint = Q[0][0]
    firstnode = 0
    for i in range(N):
        if mint > Q[i][0]:
            node = i
            mint = Q[i][0]
    # need to put this into functions instead...
    T_sim+=1000