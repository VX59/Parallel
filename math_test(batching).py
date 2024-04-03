from sympy import Matrix
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from matplotlib import colormaps as cm
# batch items if they are above the line, add them to batch buffer, if average size of batch_buffer is > model prediction for that size then send it
# this allows us to batch fragments 3 and 4, we also batch 5 and 6
# in this example for our 6 fragments we send a total of 4 post requests about 33% runtime improvement
batch = []
j = 0

sizes_posted = []
batch_sizes = []
# btach fragments lower than max of the last 64 fragments
def Batch(inputs, j:int, batch, exhausted):
    max_size = max(inputs)

    #print(max_size, inputs)
    batch.append(inputs[-1])
    print("save", max_size, inputs[-1])
    if sum(batch) > max_size or exhausted:  # exhausted will make sure we send the batch at least every window size which is the sqrt of the input space
        j += 1
        print(f"{j} send batch", sum(batch), len(batch))
        sizes_posted.append(sum(batch))
        batch_sizes.append(len(batch))

        batch = []
    
    return j, batch

n = 2**12
  # size of input space
inputs = [random.randint(0, 2048) for _ in range(n)]   # n most recent fragment sizes
#inputs = np.random.normal(2,1,n)*2044
#inputs = np.ones(n)*20
import math
bsize = 0
for i in range(1,len(inputs)):
    window = int(n)
    exhausted = i % window == 0
    if i-window >= 0:
        j, batch = Batch(inputs[i-window:i], j, batch, exhausted)
    else:
        j, batch = Batch(inputs[0:i], j, batch, exhausted)
    

plt.scatter(list(range(n)),inputs, marker=".")
print(f"{j} batches sent from {len(inputs)} fragments = {j/len(inputs)}")
print(np.average(batch_sizes))

# probability of a batch occurring after infinite fragments
print("poisson distribution: ", 1/np.e)

# show batches
print(cm.values())
batch_domain = list(range(len(sizes_posted)))
plt.xlabel("batch number")
plt.ylabel("batch size")
plt.grid(True,"major")
plt.scatter(batch_domain,sizes_posted, marker=".")
plt.savefig("batches.png")

plt.show()

x_bar = np.average(sizes_posted)
def standard_deviation(x:list):
    return ((sum((x-x_bar)**2))/n)**(1/2)

std = standard_deviation(sizes_posted)
mean = np.average(sizes_posted)
# standard deviation
print("standard deviation",std)

print("average",mean)
print("3 standard deviations", mean-3*std, mean+3*std)
