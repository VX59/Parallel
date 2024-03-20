import numpy as np

# sum a large array
def Processor(path:str):
    data = np.load(path)
    result = sum(data)
    print(result)
    data.close()
    return result
