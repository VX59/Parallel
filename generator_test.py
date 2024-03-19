import numpy as np

def Split():    # example generator for an npy file (numpy array)
    with open(path, "rb") as file:
        while True:
            fragment = file.read(1024) # the fragment size in bytes

            if not fragment:
                break

            yield np.frombuffer(fragment, dtype=np.float32)

path="downloads/test.npy"
for fragment in Split():
    print(fragment)
    input()