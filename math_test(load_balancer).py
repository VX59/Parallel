import math
import numpy as np 
import matplotlib.pyplot as plt
import random

w=2**10    # workers
m=2**10    # there are more batches than workers
# test data, the workers response times in miliseconds
# the batch sizes are in bytes
repsonse_times = pow(np.random.normal(1,random.random()*10,w),2)
batch_sizes = pow(np.random.normal(1,10,w),2)
domain = list(range(w))

mean = np.average(repsonse_times)
std = np.std(repsonse_times)
performance = (mean,std)
print(mean,std)
mean = np.average(batch_sizes)
std = np.std(batch_sizes)
batch_size = (mean,std)

print(mean, std)
def zscore(x, base):
    return (x-base[0])/base[1]

def preference(w,m):
    return (zscore(w,performance)-zscore(m,batch_size))**2

class W_info():
    def __init__(self,z,rt):
        self.z = z
        self.rt = rt
        self.assigned=None

class Pref():
    def __init__(self, z, weight, selection):
        self.weight = weight
        self.z=z
        self.assigned = None
        self.p = [] # after proposal item is removed
        self.selection = selection
        for s in selection:
            self.p.append((preference(self.z,s.z),s))
        
        self.p = sorted(self.p, key=lambda item: item[0])

workers = []
for i in range(len(repsonse_times)):
    worker = repsonse_times[i]
    z = zscore(worker,performance)

    workers.append(W_info(z, worker))

batch_prefs = []
for i in range(len(batch_sizes)):
    batch = batch_sizes[i]
    z = zscore(worker,performance)

    batch_prefs.append(Pref(z,batch,workers))

def stop_condition():
    for p in batch_prefs:
        if p.assigned == None and len(p.p) == 0:
            return True
    return False

def choose_batch():
    i = len(batch_sizes)-1
    exhausted = False
    while not exhausted:
        batch:Pref = batch_prefs[i]
        if batch.assigned == None and len(batch.p) > 0:
            return batch
        i -= 1
        if i == -1: exhausted = True

def gale_shapely():
    while True:
        batch = choose_batch()
        if batch == None:
            return
        if batch == None: return
        pref, worker = batch.p[0]
        if worker.assigned == None:
            worker.assigned = batch
            batch.assigned = worker
        else:
            prefP = preference(batch.z,worker.z)
            if prefP < pref:
                worker.assigned.p.pop(0)
                worker.assigned.assigned = None
                worker.assigned = batch
                batch.assigned = worker
            else:
                batch.p.pop(0)

gale_shapely()

x = []
y = []
for w in workers:
    if w.assigned != None:
        x.append(w.rt)
        y.append(w.assigned.weight)

# test model
def model(x):
    mx = max(batch_sizes)
    return mx/(np.exp(x/performance[1]))

print(max(x))
domain = list(range(int(max(x))))
plt.plot(domain, list(map(model, domain)), color="orange")

plt.scatter(x,y,marker=".")
plt.xlabel("worker response time in ms")
plt.ylabel("assigned batch size")
plt.savefig("assignment")
plt.show()
