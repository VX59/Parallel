from sympy import Matrix
import matplotlib.pyplot as plt
import numpy as np
# batch items if they are above the line, add them to batch buffer, if average size of batch_buffer is > model prediction for that size then send it
# this allows us to batch fragments 3 and 4, we also batch 5 and 6
# in this example for our 6 fragments we send a total of 4 post requests about 33% runtime improvement
batch = []
j = 0
def j_batch(inputs,j, batch, exhausted):

    max_size = max(inputs)
    distances = list(map(lambda x: (max_size-x)**2, inputs)) # distance from max frag size ^ 2      
    domain = list(range(len(distances)))
                #M(k**2)/2+B*k+C
    A = Matrix(list(map(lambda i: [i**2,i,1],range(len(distances)))))
    b = Matrix(list(map(lambda i: [sum(distances[:i+1])], range(len(distances)))))

    At = A.transpose()

    lhs = At*A
    rhs = At*b
    # form augmented matrix

    augment_matrix = lhs.row_join(rhs)
    x = augment_matrix.rref()
    results = x[0].col(-1)

    M=results[0]
    B=results[1]
    C=results[2]

    def result(x):
        return M*(x**2)+B*x+C

    def result_dx(x):
        return M*x+B

    linear_model = list(map(result_dx, domain))

    # this is our batch model, it describes the target 
    #plt.scatter(domain,b)
    #plt.plot(domain,b, color='black')

    #plt.plot(domain,model)
    #plt.scatter(domain,model)

    model_size = result(len(distances))

    job_size = b[-1]

    if len(distances) > 1:
        # the yellow line determines the threshold for whether or not we should send the fragment
        # the blue line represents no model where the derivative of the input size lies under the input space, therefore sends 1 fragment per batch
        d_distances = list([(distances[i+1] - distances[i]) for i in range(len(distances)-1)])
        d_distances.insert(0,0)
        #print(d_distances)
        normalized_distances = np.add(d_distances,B)
        #plt.plot(domain, linear_model, color='red')
        #plt.plot(domain,normalized_distances)
        if linear_model[-1] < normalized_distances[-1]:
            #print("batch")
            batch.append(normalized_distances[-1])

            if len(batch) > 1 and sum(batch)/len(batch) > linear_model[len(batch)] or exhausted:
               # print("send batch")
                batch = []
                j += 1
        else: 
           # print("send")
            j += 1

    return j, batch


import random

n = 100
inputs = [random.randint(0, 1000) for _ in range(n)]   # n most recent batches

for i in range(1,len(inputs)):
    exhausted = i == len(inputs)-1
    j,batch = j_batch(inputs[:i],j,batch, exhausted)
    
print(f"{j} batches sent from {len(inputs)} fragments = {j/len(inputs)}")
plt.show()