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

