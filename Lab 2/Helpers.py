from math import log
import random
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
        self.queue = []
        self.id = _id
        self.collision_counter = 0
        self.gen_arrivals()
    # Create arrival events
    def gen_arrivals(self):
        self.queue = []
        t = expn_random(self.rate) # time of first pkt arrival
        while t < self.sim_time:
            self.queue.append(t)
            t += expn_random(self.rate)
        return self.queue
    def drop_packet(self):
        d = self.queue.pop(0)
        print("node",self.id,"just dropped",d)
        self.queue[0] = max(d, self.queue[0])
class Bus:
    def __init__(self, node_list, arrival_rate=2, sim_time=1000, data_rate=20, node_distance=100, prop_speed=25, max_trans_retries=10, packet_len=5):
        self.node_list = node_list
        self.num_nodes = len(node_list)
        self.arrival_rate = arrival_rate
        self.sim_time = sim_time
        self.data_rate = data_rate
        self.node_distance = node_distance
        self.prop_speed = prop_speed
        self.prop_delay = node_distance/prop_speed
        self.max_trans_retries = max_trans_retries
        self.packet_len = packet_len
        self.trans_time = packet_len/data_rate
        self.transmitted_packets = 0
        self.current_transmitter = None
        self.successes = 0
    # return position of node in node_list with its id = node_id
    def find_node(self, node_id):
        print("looking for node with id", node_id)
        for i in range(self.num_nodes):
            if self.node_list[i].id == node_id:
                print('found at',i)
                return i
        print('not found')
        return None
    # next transmitting node
    def find_next_transmitter(self):
        # find first sending node
        firstnode = self.node_list[0]
        print('finding next transmitter')
        for i in range(self.num_nodes):
            if firstnode.queue[0] > self.node_list[i].queue[0]:
                firstnode = self.node_list[i]
        self.current_transmitter = firstnode
        print('new transmitter is node with id',self.current_transmitter.id,'with pkt time',self.current_transmitter.queue[0])
        return self.current_transmitter
    # when all nodes will consider bus busy given current transmitter node
    def bus_busy_times(self):
        node_location = self.find_node(self.current_transmitter.id)
        times = []
        transmitter_node = self.node_list[node_location]
        for i in range(self.num_nodes):
            start_time = transmitter_node.queue[0]+abs(node_location-i)*self.prop_delay
            times.append((start_time, start_time+self.trans_time))
        print("given transmitter node_id",self.current_transmitter.id,'bus is busy at:')
        print(times)
        return times
    # is there going to be a collision if the current transmitter transmits?
    def collision(self):
        times = self.bus_busy_times()
        collision = False
        for i in range(self.num_nodes):
            if self.node_list[i] is self.current_transmitter:
                continue
            if self.node_list[i].queue[0] <= times[i][0]:
                self.transmitted_packets+=1
                collision = True
            if times[i][0] < self.node_list[i].queue[0] <= times[i][1]:
                self.backoff(self.node_list[i])
                collision = True
        return collision
    def backoff(self, node):
        pkt = node.queue[0]
        node.collision_counter+=1
        if node.collision_counter > self.max_trans_retries:
            node.drop_packet()
        else:
            node.queue[0] += expn_backoff_time(node.collision_counter, self.data_rate)
    # update a node's packet times
    def update_packets(self, node):
        node_location = self.find_node(node.id)
        busy = self.bus_busy_times()[node_location]
        for t in self.node_list[node_location].queue:
            if t < busy[1]: t = busy[1]
    def transmitted(self):
        self.transmitted_packets+=1
        self.successes+=1
        self.current_transmitter.drop_packet()
        for n in self.node_list:
            self.update_packets(n)