from Helpers import Node, Bus
import csv
import multiprocessing as mp
import time

R = 1E6 # in bps
L = 1500 #bits

def sim(t):
    persistence,n, a, sim_time = t
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
    return {"n":n,"a":a,"efficiency":eff,"throughput":thru}
    # Q.put({"n":n,"a":a,"efficiency":eff,"throughput":thru})

''' def write_csv(name, result):
    with open(name,'w',newline='') as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["num_nodes", "arrival_rate", "efficiency", "throughput"])
        print('N:',n,', A:',a)
        print("efficiency",r['efficiency'])
        print("throughput",r['throughput'])
        w.writerow([n,a,r['efficiency'],r['throughput']]) '''


def question(q_num,sim_time,lk):
    N = [20*i for i in range(1,6)]
    A = [7, 10, 20]
    NA = [(n,a) for n in N for a in A]
    f = ""
    sim_protocol_type = ""
    
    p = True
    if q_num ==1:
        sim_protocol_type = '1-persistent'
        f="Q1-"+str(sim_time)+".csv"
        p = True
    elif q_num == 2:
        sim_protocol_type = 'non-persistent'
        f="Q2-"+str(sim_time)+".csv"
        p = False
    
    headstr = 'Q{} ({}), T_sim={}:'.format(q_num,sim_protocol_type, sim_time)
    # Q = mp.Queue()

    # for n in N:
    #     for a in A:
    #         p = mp.Process(target=sim, args=(p,n,a,sim_time, Q))
    #         p.start()
    #         # r = sim(p,n,a,sim_time)
    # for i in range(len(N)*len(A)):
    #     p.join()

    proc = mp.Pool(processes=15)
    data = proc.map(sim, [(p,t[0],t[1],sim_time) for t in NA])
    lk.aquire()
    print('~'*20)
    print(headstr)
    for d in data:
        print(d)
    print('~'*20)
    lk.release()

    with open(f, "w", newline='') as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["num_nodes", "arrival_rate", "efficiency", "throughput"])
        for d in data:
            w.writerow(d['n'],d['a'],d['efficiency'],d['throughput'])
    # {'n': 20, 'a': 7, 'efficiency': 0.9513121010503564, 'throughput': 0.2112555}
    
    
    # print(Q.get())

    # print('N:',n,', A:',a)
    # print("efficiency",r['efficiency'])
    # print("throughput",r['throughput'])
    
    
    ''' with open(f, "w", newline='') as f:
        w = csv.writer(f, delimiter=",")
        w.writerow(["num_nodes", "arrival_rate", "efficiency", "throughput"])
        for n in N:
            for a in A:
                r = sim(p,n,a,sim_time)
                print('N:',n,', A:',a)
                print("efficiency",r['efficiency'])
                print("throughput",r['throughput'])
                w.writerow([n,a,r['efficiency'],r['throughput']]) '''

# T_sim = 1000
# # Do for multiple T_sims
# while T_sim <= 3000:
#     print("T_sim",T_sim)
#     print('Q1:')
#     question(1, T_sim)
#     print('Q2:')
#     question(2, T_sim)
#     T_sim+=1000

if __name__ == '__main__':
    lok = mp.Lock()
    procs = []
    for i in range(1,3+1):
        proccs1 = mp.Process(target=question, args=(1,1000*i,lok)).start()
        proccs2 = mp.Process(target=question, args=(2,1000*i,lok)).start()
        procs.append(proccs1)
        procs.append(proccs2)
    for proc in procs:
        proc.join()