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
# Propagation delay
p_delay = D/S
# transmission time
trans_time = L/R

# max number of transmission retries
K_max = 10

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

# next transmitting node
def determine_next_node(Q):
    # find first sending node
    mint = Q[0][0]
    firstnode = 0
    for i in range(len(Q)):
        if mint > Q[i][0]:
            firstnode = i
            mint = Q[i][0]
    return firstnode

# calculate at what times all the nodes will consider the bus busy
def busy_bus_times(sender, pkt_timestamp, num_nodes):
    n = []
    for i in range(num_nodes):
        starttime = pkt_timestamp+abs(i-sender)*p_delay
        endtime = starttime + trans_time
        n.append((starttime,endtime))
    return n

# not sure if this is right
def expn_backoff_time(tries):
    return random.uniform(0,2**tries-1)*512/R

def persistent_sim():
    # Set up queues for each of N nodes
    Q = [gen_arrivals(A) for i in range(N)]
    
    # find first sending node
    mint = Q[0][0]
    firstnode = 0
    for i in range(N):
        if mint > Q[i][0]:
            firstnode = i
            mint = Q[i][0]
    print(firstnode)
    # firstnode is sender. Calculate time 
    # for pkt from firstnode to reach
    # every other node


# Do for multiple T_sims
while T_sim <= 3000:
    print(persistent_sim())
    T_sim+=1000