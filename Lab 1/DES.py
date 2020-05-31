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

# Create departure events
def gen_departures(arrival_events):
    prev_d_time = 0
    departure_events = []
    for ae in arrival_events:
        # pkt_len = expn_random(1/AVG_PKT_LEN)
        # service_time = pkt_len/TRANS_RATE
        service_time = gen_service_time()
        d_time = 0
        if (ae['time'] > prev_d_time):
            ''' if the current pkt arrived after the previous pkt 
                already left (ie. the queue is empty/idle) '''
            d_time = ae['time']+service_time
        else: d_time = prev_d_time + service_time
        departure_events.append({'time':d_time,'type':'departure'})
        prev_d_time = d_time
    return departure_events

# Generate service time
def gen_service_time():
    pkt_len = expn_random(1/AVG_PKT_LEN)
    service_time = pkt_len/TRANS_RATE
    return service_time
