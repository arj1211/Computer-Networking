import multiprocessing as mp

def spawned(i,n):
    print('child!',i,n)

def job(n):
    return n*n

if __name__ == '__main__':
    # for i in range(5):
    #     p = mp.Process(target=spawned, args=(i,i**2))
    #     p.start()
    #     # p.join()
    # for i in range(5):
    #     p.join()
    p = mp.Pool(processes=15)
    data = p.map(job, range(15*4))
    p.close()
    print(data)