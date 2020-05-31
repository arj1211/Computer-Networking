import random
import math
import csv

TRANS_RATE = 1E6 # C := transmission rate of output link in bps, default=1Mbps
SIM_TIME = 1000 # T := simulation time in seconds
AVG_PKT_LEN = 2000 # L := avg len of pkt in bits

# Random exponentially distributed number generator
def expn_random(rate):
    u = random.uniform(0, 1)
    x = -(1/rate) * math.log(1 - u)
    return x

# Create observer events
def gen_observers(arrival_rate):
    observer_events = []
    t = expn_random(arrival_rate*(5+random.uniform(0,2)))
    while t < SIM_TIME:
        observer_events.append({'time':t,'type':'observation'})
        t += expn_random(arrival_rate*(5+random.uniform(0,2)))
    return observer_events

# Create arrival events
def gen_arrivals(rate):
    arrival_events = []
    t = expn_random(rate) # time of first pkt arrival
    while t < SIM_TIME:
        # p = Packet(pkt_size=0,arrival_time=t,service_time=0,departure_time=0)
        arrival_events.append({'time':t,'type':'arrival'})
        t += expn_random(rate)
    return arrival_events
