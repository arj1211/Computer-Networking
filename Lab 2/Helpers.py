import collections
from math import log
import random
from collections import deque

# Exponential random number generator
def expn_random(rate):
    return (-(1/rate) * log(1 - random.uniform(0, 1)))
# Calculate backoff time based on transmission attempts and data rate
def expn_backoff_time(tries, rate):
    return random.uniform(0,(2**tries)-1)*512/rate

class Packet:
    # class representing packets in each node.
    # keeps track of arrival time, number of collisions,
    # and how often the bus is sensed to be busy
    def __init__(self, time):
        self.time = time
        self.collisions = 0
        self.bus_busy_measure = 0

    def __lt__(self,other):
        return self.time < other.time

class Node:
    # class representing a node in the LAN
    def __init__(self,_id,sim_time,arrival_rate,data_rate=1E6,max_trans_retries=10):
        self.data_rate = data_rate
        self.arrival_rate = arrival_rate
        self.sim_time = sim_time
        self.max_trans_retries = max_trans_retries
        self.queue = deque()
        self.id = _id
        self.gen_arrivals()
    
    # Create arrival events (based on technique from Lab 1)
    def gen_arrivals(self):
        t = expn_random(self.arrival_rate)
        while t < self.sim_time:
            self.queue.append(Packet(t))
            t += expn_random(self.arrival_rate)
    
    # Removes first packet from node's queue and updates arrival time of next packet
    def drop_packet(self):
        if len(self.queue)<=0: return
        d = self.queue.popleft()
        if len(self.queue)>0:
            self.queue[0].time = max(d.time, self.queue[0].time)
    
    # Applies expn backoff delay given that a node's collision counter is within threshold
    def backoff(self):
        pkt = self.queue[0]
        pkt.collisions+=1
        if pkt.collisions > self.max_trans_retries:
            self.drop_packet()
        else:
            pkt.time += expn_backoff_time(pkt.collisions, self.data_rate)

class Bus:
    # class representing the shared bus in the LAN
    def __init__(self, persistent, num_nodes, arrival_rate, sim_time, 
        data_rate=1E6, node_distance=10, prop_speed=2E8, max_trans_retries=10, packet_len=1500):
        self.persistent = persistent
        self.num_nodes = num_nodes
        self.arrival_rate = arrival_rate
        self.data_rate = data_rate
        self.sim_time = sim_time
        self.node_list = []
        self.current_transmitter = None
        self.current_transmitter_pkt = None
        self.max_trans_retries = max_trans_retries

        self.prop_delay = node_distance/prop_speed
        self.trans_time = packet_len/data_rate
        
        self.transmitted_packets = 0
        self.successes = 0

        self.init_nodes()

    # next transmitting node
    def find_next_transmitter(self):
        # find first sending node
        self.current_transmitter = None
        t = self.sim_time + 1
        for n in self.node_list:
            if len(n.queue)>0 and n.queue[0].time < min(t, self.sim_time):
                t = n.queue[0].time
                self.current_transmitter = n
                self.current_transmitter_pkt = n.queue[0]
        return self.current_transmitter
    
    # generate nodes
    def init_nodes(self):
        for i in range(self.num_nodes):
            n = Node(i, self.sim_time, self.arrival_rate)
            self.node_list.append(n)

    # when all nodes will consider bus busy given current transmitter node
    ''' def bus_busy_times(self):
        times = []
        self.find_next_transmitter()
        for i,n in enumerate(self.node_list):
            if len(n.queue)>0:
                start_time = self.current_transmitter.queue[0].time+abs(self.current_transmitter.id-i)*self.prop_delay
                times.append((start_time, start_time+self.trans_time))
        return times '''
    
    # is there going to be a collision if the current transmitter transmits?
    def collision(self):
        collision = False
        for i,n in enumerate(self.node_list):
            if n is self.current_transmitter: continue
            if len(n.queue)<=0: continue
            # times = self.bus_busy_times()
            pkt = n.queue[0]
            pd = abs(self.current_transmitter.id-i)*self.prop_delay
            if pkt.time <= self.current_transmitter_pkt.time+pd:
                self.transmitted_packets+=1
                collision = True
                n.backoff()
        if collision:
            self.transmitted_packets+=1
            self.current_transmitter.backoff()
        return collision
    
    # update packet times for all nodes
    def update_packets(self):
        for i,n in enumerate(self.node_list):
            if len(n.queue) <= 0: continue
            # if n is self.current_transmitter: continue
            # busy = self.bus_busy_times()
            pkt = n.queue[0]
            # print('current transmitter id:', self.current_transmitter.id)
            # print('transmitting packet\'s time:', self.current_transmitter.queue[0].time)
            pd = abs(self.current_transmitter.id-i)*self.prop_delay
            start_busy = self.current_transmitter_pkt.time + pd
            end_busy = start_busy + self.trans_time
            if self.persistent:
                if start_busy <= pkt.time < end_busy:
                    pkt.time = end_busy
            else:
                while start_busy <= pkt.time < end_busy:
                    if pkt.bus_busy_measure < self.max_trans_retries:
                        pkt.bus_busy_measure=+1
                    pkt.time+=expn_backoff_time(pkt.bus_busy_measure, self.data_rate)
                pkt.bus_busy_measure=0
            
    # call when packet successfully transmitted
    def transmitted(self):
        self.transmitted_packets+=1
        self.successes+=1
        self.current_transmitter.drop_packet()
        self.update_packets()