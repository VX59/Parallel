import numpy as np

# add the result fragments to a list
def Merge(resourcepath, resultpath):
    data = np.load(resourcepath)

    with open(resultpath, "ab") as file:
        np.save(file, data)