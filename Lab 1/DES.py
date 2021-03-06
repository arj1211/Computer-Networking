from math import log
import csv
import heapq
import random

TRANS_RATE = 1E6 # C := transmission rate of output link in bps, default=1Mbps
SIM_TIME = 1000 # T := simulation time in seconds
AVG_PKT_LEN = 2000 # L := avg len of pkt in bits

# headers meant for csv tables
TITLES = ["Queue_Util", "N_a", "N_d", "N_o", "P_idle", "E[N]"]
TITLES_K = ["Queue_Util", "Buff_size", "N_a", "N_d", "N_o", "P_idle", "E[N]", "P_loss"]

''' a wrapper class for event time and type. 
    Used for M/M/1/K because heapq needs comparable objects.
    The dictionary approach from M/M/1 using a lambda to sort by time
    doesn't work because heapq doesn't have an option to specify
    a comparator key ''' 
class Event:
    def __init__(self,etime,etype):
        self.time=etime
        self.type=etype
    # the __lt__ (less than) function defines
    #   comparison for this wrapper class
    def __lt__(self, value):
        self.time<value.time

# Exponential random number generator
def expn_random(rate):
    return (-(1/rate) * log(1 - random.uniform(0, 1)))

# Create observer events
def gen_observers(arrival_rate):
    observer_events = []
    ''' arrival_rate*(5+random.uniform(0,2)) is used because
    observer events must be at minimum 5 times the rate of 
    arrival/departure events. '''
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
        arrival_events.append({'time':t,'type':'arrival'})
        t += expn_random(rate)
    return arrival_events

# Create departure events
def gen_departures(arrival_events):
    prev_d_time = 0
    departure_events = []
    for ae in arrival_events:
        service_time = gen_service_time()
        d_time = 0
        if (ae['time'] > prev_d_time):
            ''' if the current pkt arrived after the previous pkt 
                already left (ie. the queue is empty/idle) '''
            d_time = ae['time']+service_time
        else:
            d_time = prev_d_time + service_time
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
        events = sorted(a+gen_departures(a)+gen_observers(rate),
            key=lambda e: e['time'])
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
    # the 'source' where 'the next packet' is grabbed
    event_list = gen_events(arrival_rate)
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
    # P_idle := how often was the queue empty out of the
    #   total times we checked it?
    P_idle = idle_count/pkt_type_count['observation']
    # time average of # of packets in queue; E[N]
    TIME_AVG_PKTS_IN_Q = sum(q_len_observed_over_time)/len(q_len_observed_over_time)
    return {TITLES[0]:q_util,
            TITLES[1]:pkt_type_count['arrival'],
            TITLES[2]:pkt_type_count['departure'],
            TITLES[3]:pkt_type_count['observation'],
            TITLES[4]:P_idle,
            TITLES[5]:TIME_AVG_PKTS_IN_Q}

# Simulate M/M/1/K
def simulateMM1K(q_util, K):
    pkt_type_count = {
        'arrival':0, # N_a
        'departure':0, # N_d
        'observation':0 # N_o
    }
    idle_count = 0
    q_len_observed_over_time = []
    current_queue_length = 0
    pkts_lost_count = 0
    prev_d_time = 0
    arrival_rate = q_util*TRANS_RATE/AVG_PKT_LEN
    event_list = gen_events(arrival_rate, K)
    # converts events stored as dictionaries to Event 
    #   objects for use with heapq
    event_list = [Event(e['time'],e['type']) for e in event_list]
    # an initial heapifying of the event list, 
    #   maintaining the heap invariant: event time
    heapq.heapify(event_list)
    while len(event_list) > 0:
        pkt = heapq.heappop(event_list)
        if pkt.type=='arrival':
            if current_queue_length < K:
                serv_time = gen_service_time()
                d_time = 0
                if current_queue_length > 0:
                    d_time = prev_d_time + serv_time
                else:
                    d_time = pkt.time + serv_time
                prev_d_time = d_time
                heapq.heappush(event_list,Event(d_time,'departure'))
                pkt_type_count[pkt.type]+=1
                current_queue_length+=1
            else:
                pkts_lost_count+=1
        elif pkt.type=='departure':
            current_queue_length-=1
            pkt_type_count[pkt.type]+=1
        else:
            pkt_type_count[pkt.type]+=1
            # an observer event. observe q_len and save that info
            q_len_observed_over_time.append(current_queue_length)
            # if q empty right now, its idle
            if current_queue_length==0:
                idle_count+=1
    P_idle = idle_count/pkt_type_count['observation']
    TIME_AVG_PKTS_IN_Q = sum(q_len_observed_over_time)/len(q_len_observed_over_time)
    # P_loss := ratio of packets lost to total packets attempting to arrive
    P_loss = pkts_lost_count/(pkt_type_count['arrival']+pkts_lost_count)
    return {TITLES_K[0]:q_util,
            TITLES_K[1]:K,
            TITLES_K[2]:pkt_type_count['arrival'],
            TITLES_K[3]:pkt_type_count['departure'],
            TITLES_K[4]:pkt_type_count['observation'],
            TITLES_K[5]:P_idle,
            TITLES_K[6]:TIME_AVG_PKTS_IN_Q,
            TITLES_K[7]:P_loss}

# Q1
def question1(f_name='q1.csv', w_type='w'):
    print('-'*10)
    print('Question 1:')
    lam = 75 # lambda
    # list comprehension of 1000 exponential 
    #   random vars based on lambda
    randomvars = [expn_random(lam) for i in range(1000)]
    mean = sum(randomvars)/len(randomvars)
    variance = sum( [(r - mean) ** 2 for r in randomvars] ) / len(randomvars)
    print('Mean',mean)
    print('Variance',variance)
    print('-'*10)
    with open(f_name, w_type, newline='') as f:
        w = csv.writer(f, dialect='excel', delimiter=',')
        w.writerow(['Mean','Variance'])
        w.writerow([mean,variance])

# Q3
def question3(f_name='q3.csv', w_type='w'):
    print('-'*10)
    print('Question 3:')
    # 0.25 through 0.95
    q_util_list = [i/100 for i in range(25,105,10)]
    # hold results returned from simulation iterations
    results = []
    for i in q_util_list:
        results.append(simulateMM1(i))
        print('~'*10)
        for t in TITLES:
            print(t,results[-1][t])
    print('-'*10)
    with open(f_name, w_type, newline='') as f:
        w = csv.writer(f, dialect='excel', delimiter=',')
        w.writerow(TITLES)
        for r in results:
            w.writerow([r[t] for t in TITLES])

# Q4
def question4(f_name='q4.csv', w_type='w'):
    print('-'*10)
    print('Question 4:')
    q_util = 1.2
    result = simulateMM1(q_util)
    for t in TITLES:
        print(t,result[t])
    print('-'*10)
    with open(f_name, w_type, newline='') as f:
        w = csv.writer(f, dialect='excel', delimiter=',')
        w.writerow(TITLES)
        w.writerow([result[t] for t in TITLES])

# Q6
def question6(f_name='q6.csv', w_type='w'):
    print('-'*10)
    print('Question 6:')
    # 0.5 through 1.5
    q_util_list = [i/100 for i in range(50,160,10)]
    # buffer sizes
    K_list = [10,25,50]
    results=[]
    for q_util in q_util_list:
        for K in K_list:
            results.append(simulateMM1K(q_util,K))
            print('~'*10)
            for t in TITLES_K:
                print(t,results[-1][t])
    print('-'*10)
    with open(f_name, w_type, newline='') as f:
        w = csv.writer(f, dialect='excel', delimiter=',')
        w.writerow(TITLES_K)
        for r in results:
            w.writerow([r[t] for t in TITLES_K])

question1()
question3()
question4()
question6()
SIM_TIME = 2000
question3(w_type='a')
question4(w_type='a')
question6(w_type='a')