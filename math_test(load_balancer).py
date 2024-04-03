import math
import numpy as np 
import matplotlib.pyplot as plt
import random

w=2**11    # workers
# test data, the workers response times in miliseconds
scale=10
repsonse_times = pow(np.random.normal(scale,random.random()*scale,w),2)
domain = list(range(w))


mean = np.average(repsonse_times)
std = np.std(repsonse_times)
print(std)

# determine if a worker should get kicked

def kick(x:int):
    if x > (mean + 4*std):
        print(x)
        return x

kicked = [kick(i) for i in repsonse_times]
print(kicked)

plt.xlabel("workers")
plt.ylabel("response time ms")
plt.scatter(domain, repsonse_times, marker=".")
plt.scatter(domain, kicked, marker="x", color='red')
plt.savefig("autobalance")
plt.show()
