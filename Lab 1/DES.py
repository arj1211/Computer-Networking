import random
import math
import csv

TRANS_RATE = 1E6 # C := transmission rate of output link in bps, default=1Mbps
SIM_TIME = 1000 # T := simulation time in seconds
AVG_PKT_LEN = 2000 # L := avg len of pkt in bits

TITLES = ["Queue_Util", "N_a", "N_d", "N_o", "P_idle", "E[N]"]

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

# Generate all events for M/M/1 by default, M/M/1/K if K > 0
def gen_events(rate, K=0):
    events = []
    if K == 0:
        # Infinite queue case
        a = gen_arrivals(rate)
        events = sorted(a+gen_departures(a)+gen_observers(rate), key=lambda e: e['time'])
    else:
        # Finite queue case
        a = gen_arrivals(rate)
        events = sorted(a+gen_observers(rate), key=lambda e: e['time'])
    return events

# Simulate M/M/1
def simulateMM1(q_util):
    pkt_type_count = {
        'arrival':0, # N_a
        'departure':0, # N_d
        'observation':0 # N_o
    }
    idle_count = 0
    current_queue_length = 0
    q_len_observed_over_time = []
    arrival_rate = q_util*TRANS_RATE/AVG_PKT_LEN
    event_list = gen_events(arrival_rate) # the 'source' where 'the next packet' is grabbed
    ''' 'q' represents the queue where packets arrive at and depart from. 
        We don't need an actual structure for it in this 
        case since its size is infinite. '''
    for pkt in event_list:
        # What type of event is it? count it
        pkt_type_count[pkt['type']]+=1
        if pkt['type']=='arrival': current_queue_length+=1
        elif pkt['type']=='departure': current_queue_length-=1
        else:
            # an observer event. observe q_len and save that info
            q_len_observed_over_time.append(current_queue_length)
            # if q empty right now, its idle
            if current_queue_length==0: idle_count+=1
    # P_idle := how often was the queue empty out of the total times we checked it?
    P_idle = idle_count/pkt_type_count['observation']
    TIME_AVG_PKTS_IN_Q = sum(q_len_observed_over_time)/len(q_len_observed_over_time)
    return {TITLES[0]:q_util,
            TITLES[1]:pkt_type_count['arrival'],
            TITLES[2]:pkt_type_count['departure'],
            TITLES[3]:pkt_type_count['observation'],
            TITLES[4]:P_idle,
            TITLES[5]:TIME_AVG_PKTS_IN_Q}

# Q1
def question1(f_name='q1.csv', w_type='w'):
    rate = 75
    iters = int(1E3)
    randomvars = [expn_random(rate) for i in range(iters)]
    mean = sum(randomvars)/len(randomvars)
    variance = sum( [(x - mean) ** 2 for x in randomvars] ) / len(randomvars)
    with open(f_name, w_type, newline='') as f:
        w = csv.writer(f, dialect='excel', delimiter=',')
        w.writerow(['Mean','Variance'])
        w.writerow([mean,variance])
