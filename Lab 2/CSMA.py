from Helpers import Node, Bus
import csv

def sim(persistence,n, a, R, L, sim_time):
    # set up the nodes and bus
    bus = Bus(persistence, n, a, sim_time)
    # while there exists a next transmitting node
    while bus.find_next_transmitter():
        # check if a collision will occur
        c = bus.collision()
        # if no collision occurs, we have a 
        # successful transmission
        if not c:
            bus.transmitted()
    eff = bus.successes/bus.transmitted_packets
    thru = bus.successes*L / (sim_time * R)
    return {"efficiency":eff,"throughput":thru}

def question(q_num,sim_time):
    N = [20*i for i in range(1,6)]
    A = [7, 10, 20]
    R = 1E6 # in bps
    L = 1500 #bits
    f = ""
    p = True
    if q_num ==1:
        print('1-persistent')
        f="Q1-"+str(sim_time)+".csv"
        p = True
    elif q_num == 2:
        print('non-persistent')
        f="Q2-"+str(sim_time)+".csv"
        p = False
    with open(f, "w", newline='') as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["num_nodes", "arrival_rate", "efficiency", "throughput"])
        for n in N:
            for a in A:
                print('N:',n,', A:',a)
                r = sim(p,n,a,R,L,sim_time)
                print("efficiency",r['efficiency'])
                print("throughput",r['throughput'])
                w.writerow([n,a,r['efficiency'],r['throughput']])

T_sim = 1000
# Do for multiple T_sims
while T_sim <= 3000:
    print("T_sim",T_sim)
    print('Q1:')
    question(1, T_sim)
    print('Q2:')
    question(2, T_sim)
    T_sim+=1000