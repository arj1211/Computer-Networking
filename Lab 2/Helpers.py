import collections
from math import log
import random
from collections import deque

# Exponential random number generator
def expn_random(rate):
    return (-(1/rate) * log(1 - random.uniform(0, 1)))
# not sure if this is right
def expn_backoff_time(tries, R):
    return random.uniform(0,2**tries-1)*512/R
class Node:
    def __init__(self, rate, sim_time, _id):
        self.rate = rate
        self.sim_time = sim_time
        self.queue = deque()
        self.id = _id
        self.collision_counter = 0
        self.gen_arrivals()
    # Create arrival events
    def gen_arrivals(self):
        t = expn_random(self.rate) # time of first pkt arrival
        while t < self.sim_time:
            self.queue.append(t)
            t += expn_random(self.rate)
        return self.queue
    def drop_packet(self):
        if len(self.queue)>0:
            d = self.queue.popleft()
            if len(self.queue)>0:
                self.queue[0] = max(d, self.queue[0])
    def backoff(self):
        pkt = self.queue[0]
        self.collision_counter+=1
        if self.collision_counter > self.max_trans_retries:
            self.drop_packet()
        else:
            self.queue[0] += expn_backoff_time(self.collision_counter, self.data_rate)

class Bus:
    def __init__(self, persistent, num_nodes, arrival_rate=2, sim_time=1000, 
        data_rate=1, node_distance=10, prop_speed=(2/3)*(3E8), max_trans_retries=10, packet_len=1500):
        self.persistent = persistent
        self.node_list = []
        for i in range(num_nodes):
            n = Node(arrival_rate, sim_time, i)
            n.gen_arrivals()
            self.node_list.append(n)
        self.arrival_rate = arrival_rate
        self.sim_time = sim_time
        self.data_rate = data_rate
        self.node_distance = node_distance
        self.prop_speed = prop_speed
        self.max_trans_retries = max_trans_retries
        self.packet_len = packet_len

        self.prop_delay = node_distance/prop_speed
        self.trans_time = packet_len/data_rate
        
        self.transmitted_packets = 0
        self.current_transmitter = None
        self.successes = 0
    
    # next transmitting node
    def find_next_transmitter(self):
        # find first sending node
        self.current_transmitter = None
        t = self.sim_time + 1
        for n in self.node_list:
            if len(n.queue)>0 and n.queue[0] < t:
                t = n.queue[0]
                self.current_transmitter = n
        return self.current_transmitter
    
    # when all nodes will consider bus busy given current transmitter node
    def bus_busy_times(self):
        times = []
        for i,n in enumerate(self.node_list):
            if len(n.queue)>0:
                start_time = self.current_transmitter.queue[0]+abs(self.current_transmitter.id-i)*self.prop_delay
                times.append((start_time, start_time+self.trans_time))
        return times
    
    # is there going to be a collision if the current transmitter transmits?
    def collision(self):
        times = self.bus_busy_times()
        collision = False
        for i,n in enumerate(self.node_list):
            if n is self.current_transmitter: continue
            if len(n.queue)<=0: continue
            if n.queue[0] < times[i][0]:
                self.transmitted_packets+=1
                collision = True
                n.backoff()
        if collision:
            self.transmitted_packets+=1
            self.current_transmitter.backoff()
        return collision
    
    # update packet times for all nodes
    def update_packets(self):
        busy = self.bus_busy_times()
        for i,n in enumerate(self.node_list):
            if len(n.queue) <= 0: continue
            if n is self.current_transmitter: continue
            if busy[i][0] <= n.queue[0] <= busy[i][1]:
                for pkt in n.queue:
                    pkt = max(pkt, busy[i][1])
            
    # call when packet successfully transmitted
    def transmitted(self):
        self.transmitted_packets+=1
        self.successes+=1
        self.current_transmitter.drop_packet()
        self.update_packets()