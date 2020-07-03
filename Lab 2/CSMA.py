from Helpers import Node, Bus
# The number of nodes/computers connected to the LAN (variable).
# N = 10
# Average packet arrival rate (packets/second) (variable). 
# Data packets arrive at the MAC layer following a Poisson 
# process at all nodes.
# A = 2
# The speed of the LAN/channel/bus (fixed).
# R = 20
# Packet length (fixed).
# L = 5
# Distance between adjacent nodes on the bus/channel.
D = 10
# Propagation speed
S = (2/3)*(3E8)
# Propagation delay
# p_delay = D/S
# transmission time
# trans_time = L/R
# max number of transmission retries
K_max = 10
# simulation time
T_sim = 1000

def persistent_sim(n, a, R, L):
    # set up the nodes and bus
    node_list = [Node(rate=a, sim_time=T_sim, _id=i) for i in range(n)]
    bus = Bus(node_list, a, T_sim, R, D, S, K_max, L)
    while bus.find_next_transmitter():
        if not bus.collision():
            bus.transmitted()
    eff = bus.successes/bus.transmitted_packets
    thru = bus.successes*L / (T_sim * R)
    print("eff",eff)
    print("thru",thru)
    return {"eff":eff,"thru":thru}


def q1():
    N = [20*i for i in range(1,6)]
    A = [7, 10, 20]
    R = 1 #Mbps
    L = 1500 #bits
    for n in N:
        for a in A:
            print("N",n,"A",a)
            persistent_sim(n,a,R,L)

# Do for multiple T_sims
while T_sim <= 3000:
    print("T_sim",T_sim)
    print(q1())
    T_sim+=1000