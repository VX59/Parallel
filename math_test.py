from sympy import Matrix
import matplotlib.pyplot as plt

max_size = 2048
A = Matrix([[1,1],
           [2,1],
           [3,1],
           [4,1]
           ])

b = Matrix([[max_size-500],
           [max_size-850],
           [max_size-600],
           [max_size-520]
           ])

At = A.transpose()

lhs = At*A
rhs = At*b
# form augmented matrix

augment_matrix = lhs.row_join(rhs)
x = augment_matrix.rref()
print(x)
results = x[0].col(-1)

M=results[0]
B=results[1]

def result(x):
    return M*x+B

model = list(map(result, [1,2,3,4]))

plt.scatter([1,2,3,4],[[max_size-500],
           [max_size-850],
           [max_size-600],
           [max_size-520]
           ])

plt.plot([1,2,3,4],model)
plt.show()

# i Have a new input i want to map and i want to find the batch size
new_b = Matrix([[max_size-500],
           [max_size-850],
           [max_size-600],
           [max_size-520],
           [max_size-430],
           [max_size-278]
           ])

new_A = A = Matrix([[1,1],
                    [2,1],
                    [3,1],
                    [4,1],
                    [5,1],
                    [6,1]
                    ])

new_At = new_A.transpose()

lhs = new_At*new_A
rhs = new_At*new_b
# form augmented matrix

augment_matrix = lhs.row_join(rhs)
x = augment_matrix.rref()
print(x)
results = x[0].col(-1)

M=results[0]
B=results[1]

model = list(map(result, [1,2,3,4,5,6]))

plt.scatter([1,2,3,4,5,6],[[max_size-500],
           [max_size-850],
           [max_size-600],
           [max_size-520],
           [max_size-430],
           [max_size-278]
           ])

plt.scatter([6],[result(6)])

plt.plot([1,2,3,4,5,6],model)
plt.show()

print(result(2))

# batch items if they are above the line, add them to batch buffer, if average size of batch_buffer is > model prediction for that size then send it
# this allows us to batch fragments 3 and 4, we also batch 4 and 5
# in this example for our 6 fragments we send a total of 4 post requests about 33% runtime improvement