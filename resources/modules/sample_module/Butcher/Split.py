def Split(path:str):    # example generator for an npy file (numpy array)
    with open(path, "rb") as file:
        while True:
            fragment:bytes = file.read(128) # the fragment size in bytes

            if not fragment:
                break

            yield fragment