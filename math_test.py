from sympy import Matrix
import matplotlib.pyplot as plt
import numpy as np
import random
# batch items if they are above the line, add them to batch buffer, if average size of batch_buffer is > model prediction for that size then send it
# this allows us to batch fragments 3 and 4, we also batch 5 and 6
# in this example for our 6 fragments we send a total of 4 post requests about 33% runtime improvement
batch = []
j = 0

sizes_posted = []

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

        batch = []
    
    return j, batch

n = 2**10  # size of input space
inputs = [random.randint(0, 1000) for _ in range(n)]   # n most recent fragment sizes
import math
bsize = 0
for i in range(1,len(inputs)):
    window = int(math.sqrt(n))
    exhausted = i % window == 0
    if i-window >= 0:
        j, batch = Batch(inputs[i-window:i], j, batch, exhausted)
    else:
        j, batch = Batch(inputs[0:i], j, batch, exhausted)
    
print(f"{j} batches sent from {len(inputs)} fragments = {j/len(inputs)}")

plt.ylabel("batch size")
plt.xlabel("input space")
plt.scatter(list(range(len(inputs))), inputs, color="red")
plt.scatter(list(range(len(sizes_posted))), sizes_posted)
plt.show()
