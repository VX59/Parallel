import numpy as np

def Processor(path:str):
    data = np.load(path)
    result = sum(data)
    print(result)
    data.close()
    return result
